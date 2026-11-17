"""Aegis PLE: evidence-first engineering agent with deliverable verification.

The model sees the entire task, can use an isolated task container over the PLE
protocol and can access MCP applications exposed with the task. No web queries,
external tools or task-specific hard-coded answers.
"""
from __future__ import annotations
import asyncio
import json
import os
import re
import time
from typing import Any
import openai
from mcp_bridge import MCPBridge
from protocol import TaskCancelled, TaskFailure

MAX_TURNS = int(os.getenv('MAX_AGENT_TURNS', '140'))
VERIFY_RESERVE = int(os.getenv('VERIFY_RESERVE_SEC', '180'))
MAX_TOKENS = int(os.getenv('MAX_COMPLETION_TOKENS','12000'))
VERIFY_GATE = os.getenv('VERIFY_GATE', '1') == '1'
ENABLE_INVENTORY = os.getenv('ENABLE_INVENTORY', '1') == '1'
MAX_RESULT = 17000
CONTEXT_PAT = re.compile(r'(context|prompt).{0,80}(length|window|long|tokens)|maximum prompt length', re.I)
RETRY = (3, 8, 16, 30, 60)

SYSTEM = '''You are Aegis PLE, a senior multidisciplinary physical engineering analyst.
You work on one genuine project in an offline Linux task container; your tools run
in that task container, not inside your model host. Your responsibility is to
produce actual, correct deliverable files, not merely describe how to make them.

WORKING PROCEDURE (must be adapted to the task, no fixed answers):
1) Read ALL task constraints. Inventory the relevant files and extract exact
   expected output paths/formats; open drawings, specifications, tables and source data.
2) Form a compact plan linked to each required deliverable and its acceptance tests.
   Prioritize producing a complete minimally correct result before refinements.
3) Ground every numerical value in source evidence. Maintain an explicit register
   of quantities/units, design assumptions, reference versions, load cases, code
   clauses and cross-sheet identifiers. Never invent a code citation.
4) Use installed engineering/office tools (Python scientific stack if available,
   LibreOffice, CAD/IFC/geometry tools, pdftotext, etc). Check availability first.
   For all quantitative results, write executable verification scripts or
   spreadsheet formulas when appropriate. Run solvers rather than mental arithmetic.
5) Cross-check results independently: dimensional analysis and SI/US unit
   conversions, boundary conditions, signed forces, electrical phase/current,
   tolerances, clearance, document references, source-to-result consistency.
6) Create deliverables at the EXACT requested paths; do not hide content in
   commentary. Reopen generated output, test format and numerical values, and
   resolve discrepancies. Label unverified assumptions; do not fabricate results.
7) For MCP app tasks, list server tools before calling them; use task MCP, not
   shell requests to external hosts. Respect file, network and resource limits.
8) Finish with a concise file/path checklist and key computed findings,
   distinguishing verified from uncertain outputs.

ENGINEERING DISCIPLINES:
- Structural: model load combinations, paths, units, supports, deflections,
  geometries, sections, stability, and code edition/reference.
- Civil: coordinate reference systems, grades, hydraulics, settlement and soil
  parameters, drawing grid/location consistency and report math.
- Electrical: per-phase vs line values, voltage drops, current and power factor,
  protection ratings, equipment schedules and source-to-one-line integrity.
- Mechanical: mass/energy balances, loads, efficiencies, flow rates, pressure
  drops, pipe/dimension clearances, lifecycle scenarios and cost assumptions.

Do NOT alter any grading scripts, game evaluation, or hidden evaluation files.
Do not install new packages from the internet at task runtime. Do not claim a
license sign-off or code approval. Respect the task's user-provided constraints.
'''

TOOLS = [
    {'type':'function', 'function':{'name':'bash','description':'Run shell command in task container; use this for python calculations, document/CAD conversion and output validation. Each command starts in task workdir.',
        'parameters':{'type':'object','properties':{'command':{'type':'string'},'timeout_sec':{'type':'integer','minimum':1,'maximum':600}},'required':['command']}}},
    {'type':'function', 'function':{'name':'read_file','description':'Read a UTF-8 text file inside task container. For binary files use bash conversion or base64.',
        'parameters':{'type':'object','properties':{'path':{'type':'string'}},'required':['path']}}},
    {'type':'function', 'function':{'name':'write_file','description':'Write complete text output to task container, creating parents if required. Prefer bash for large generated files.',
        'parameters':{'type':'object','properties':{'path':{'type':'string'},'content':{'type':'string'}},'required':['path','content']}}},
    {'type':'function', 'function':{'name':'mcp_list','description':'Discover available tools in the named task MCP server. Only available if task advertises MCP servers.',
        'parameters':{'type':'object','properties':{'server':{'type':'string'}},'required':['server']}}},
    {'type':'function', 'function':{'name':'mcp_call','description':'Call a discovered task MCP tool with schema-valid arguments.',
        'parameters':{'type':'object','properties':{'server':{'type':'string'},'tool':{'type':'string'},'arguments':{'type':'object'}},'required':['server','tool','arguments']}}},
]

def clip(v: str, limit=MAX_RESULT):
    if len(v) <= limit: return v
    half = limit//2
    return v[:half] + f'\n...[{len(v)-limit} chars omitted]...\n' + v[-half:]

def compact(messages: list[dict[str, Any]]):
    """Compress old tool results; do not mutate signed assistant replies."""
    prior = [m for m in messages[:-6] if m.get('role') == 'tool' and isinstance(m.get('content'), str) and len(m['content']) > 1400]
    if not prior: return False
    for msg in prior[:max(1, len(prior)//2)]:
        msg['content'] = msg['content'][:600] + '\n[Earlier verbose tool result removed; re-read source if needed]'
    return True

def marked(messages, model):
    if 'claude' not in model.lower(): return messages
    out = list(messages)
    for idx in {0,len(out)-1}:
        if isinstance(out[idx].get('content'), str) and out[idx]['content']:
            out[idx] = {**out[idx], 'content':[{'type':'text','text':out[idx]['content'],
                'cache_control':{'type':'ephemeral'}}]}
    return out

async def run_tool(session, mcp, call):
    name = call.function.name
    try:
        args = json.loads(call.function.arguments or '{}')
        if not isinstance(args, dict): raise ValueError('Arguments must be an object')
        if name == 'bash':
            command = args['command']
            if not isinstance(command,str) or not command.strip(): raise ValueError('Empty bash command')
            result = await session.exec(command, int(args.get('timeout_sec', 120)))
            return clip(f'exit_code={result.get("exit_code")} timed_out={result.get("timed_out",False)} truncated={result.get("truncated",False)}\n{result.get("output","")}')
        if name == 'read_file':
            data = await session.read_file(args['path'])
            return clip(data.decode('utf-8','replace'))
        if name == 'write_file':
            content = args['content'].encode('utf-8')
            return f'wrote {await session.write_file(args["path"], content)} bytes to {args["path"]}'
        if name == 'mcp_list':
            return clip(json.dumps(await mcp.list_tools(args['server']),ensure_ascii=False), 45000)
        if name == 'mcp_call':
            return clip(json.dumps(await mcp.call_tool(args['server'],args['tool'],args['arguments']), ensure_ascii=False))
        return 'Error: unknown tool'
    except (KeyError,ValueError,TaskFailure,TaskCancelled,RuntimeError,TypeError) as e:
        return f'Tool error: {type(e).__name__}: {str(e)[:600]}'

async def model_call(client, session, messages, use_tools, model):
    attempts = 0
    while True:
        left = session.time_left()
        if left is not None and left <= 3: raise TaskCancelled('Deadline imminent')
        try:
            req = dict(model=model, messages=marked(messages,model),
                       max_completion_tokens=MAX_TOKENS, tools=TOOLS)
            if use_tools:
                req.update(tool_choice='auto')
            else:
                req.update(tool_choice='none')
            # Keep model compatibility broad: no reasoning_effort parameter
            # (unsupported by some sponsored models).
            reply = await asyncio.wait_for(client.chat.completions.create(**req),
                         timeout=min(1600, max(4, left-(3 if not use_tools else VERIFY_RESERVE))) if left is not None else 1600)
            if reply.usage:
                details = getattr(reply.usage,'prompt_tokens_details',None)
                await session.usage(model,reply.usage.prompt_tokens or 0,
                                    reply.usage.completion_tokens or 0,
                                    getattr(details,'cached_tokens',0) or 0)
            return reply
        except (openai.APIError,asyncio.TimeoutError) as e:
            status = getattr(e,'status_code', None)
            if status == 400 and CONTEXT_PAT.search(str(e)) and compact(messages):
                await session.log('Context reduced after model context-limit error')
                continue
            if status is not None and status < 500 and status not in (408,409,429):
                raise
            if attempts >= len(RETRY): raise
            delay = RETRY[attempts]; attempts += 1
            left = session.time_left()
            if left is not None and left <= delay + 10: raise
            await session.log(f'Model retry {attempts} after {type(e).__name__}')
            await asyncio.sleep(delay)

async def solve(session, client=None):
    model = os.getenv('MODEL_NAME')
    if not model: raise RuntimeError('MODEL_NAME not set; evaluator injects it')
    own_client = client is None
    if own_client:
        client = openai.AsyncOpenAI(timeout=1650, max_retries=2)
    mcp = MCPBridge(session)
    mcp_names = ', '.join(session.mcp_servers) or 'none'
    messages = [
      {'role':'system', 'content': SYSTEM + f'\nTASK WORKDIR: {session.workdir}\nMCP SERVERS: {mcp_names}'},
      {'role':'user', 'content': session.instruction}
    ]
    final = ''
    verification_injected = False
    preliminary = None
    try:
        # Prioritize a minimal fast inventory to reduce hallucinated file names.
        if ENABLE_INVENTORY:
            inventory = await session.exec('pwd; ls -la; find . -maxdepth 2 -type f -printf "%p (%s bytes)\\n" 2>/dev/null | head -100', 30)
            messages.append({'role':'user','content':'Initial task-container inventory (not exhaustive):\n'+clip(inventory.get('output',''),9000)})
        for turn in range(MAX_TURNS):
            left = session.time_left()
            wrap = left is not None and left < max(35, VERIFY_RESERVE)
            if session.cancelled.is_set(): break
            if wrap:
                messages.append({'role':'user','content':'Deadline is near. Finalize deliverables now. Report paths and uncertain items concisely; no additional operations.'})
            elif turn and turn % 18 == 0:
                messages.append({'role':'user','content':'Checkpoint: verify remaining requested deliverables, source references, numerical units and output paths. Keep moving toward complete files.'})
            reply = await model_call(client,session,messages,not wrap,model)
            choice = reply.choices[0]
            msg = choice.message
            reply_text = msg.content or ''
            if reply_text:
                preliminary = reply_text
                session.last_summary = reply_text
            messages.append(msg.model_dump(exclude_none=True))
            calls = msg.tool_calls or []
            if not calls or wrap:
                if choice.finish_reason == 'length' and not wrap:
                    messages.append({'role':'user','content':'Continue from the truncated reply and complete the task. If no tools are needed, provide the final output checklist.'})
                    continue
                if VERIFY_GATE and not verification_injected and not wrap and turn < MAX_TURNS-2:
                    verification_injected = True
                    # One mandatory independent verification pass after model
                    # would otherwise stop, to reduce premature completion.
                    verify = await session.exec('find . -maxdepth 4 -type f -printf "%p (%s bytes)\\n" 2>/dev/null | tail -100', 30)
                    messages.append({'role':'user','content':'QUALITY GATE: You appear finished. Before stopping, verify each required output is present, nonempty and readable, validate units/calculations and check task-specific filenames. Here is the current file listing:\n'+clip(verify.get('output',''),8000)+'\nIf anything needs fixing, use tools. Otherwise reply with a definitive output checklist.'})
                    continue
                if reply_text:
                    final = reply_text
                    break
                messages.append({'role':'user','content':'Please provide a concise final deliverables summary with exact paths.'})
                continue
            # No more than four remote commands at once; prevents exhausting
            # task-container processes and stays inside evaluator 8-call limit.
            for group_start in range(0,len(calls),4):
                group = calls[group_start:group_start+4]
                outputs = await asyncio.gather(*(run_tool(session,mcp,c) for c in group))
                for c, result in zip(group,outputs):
                    messages.append({'role':'tool','tool_call_id':c.id,'content':result})
            if turn > 0 and turn % 25 == 0:
                compact(messages)
        else:
            final = preliminary or f'Turn budget exhausted ({MAX_TURNS}). Please inspect files in {session.workdir}.'
        return final or preliminary or 'No final written deliverable summary; inspect task container files.'
    finally:
        if own_client:
            await client.close()
