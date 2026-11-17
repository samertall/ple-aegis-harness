import asyncio
import json
import os
from types import SimpleNamespace
import pytest
from harness import solve, clip, compact
from mcp_bridge import MCPBridge

class Message:
    def __init__(self, content=None, tools=None):
        self.content = content
        self.tool_calls = tools or []
    def model_dump(self, exclude_none=True):
        obj = {'role':'assistant', 'content':self.content}
        if self.tool_calls:
            obj['tool_calls']=[{'id':c.id,'type':'function','function':{'name':c.function.name,'arguments':c.function.arguments}} for c in self.tool_calls]
        return obj

def toolcall(name, payload, call_id='t1'):
    return SimpleNamespace(id=call_id,function=SimpleNamespace(name=name,arguments=json.dumps(payload)))

class FakeModel:
    def __init__(self):
        self.calls = []
        self.answers = [Message(tools=[toolcall('write_file',{'path':'/app/out/report.md','content':'Verified output'})]),
                        Message(content='Files completed.'),
                        Message(content='Verified /app/out/report.md: report exists.')]
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
    async def create(self, **kwargs):
        self.calls.append(kwargs)
        msg=self.answers.pop(0)
        return SimpleNamespace(usage=None,choices=[SimpleNamespace(message=msg,finish_reason='stop')])

class FakeSession:
    workdir='/app'
    instruction='Write /app/out/report.md containing Verified output'
    mcp_servers={}
    cancelled=asyncio.Event()
    last_summary=''
    def __init__(self):
        self.files = {}
        self.commands = []
    def time_left(self): return 500
    async def exec(self, command, timeout=120):
        self.commands.append(command)
        return {'exit_code':0,'output':'/app\n./data.csv (42 bytes)\n./out/report.md (15 bytes)' if self.files else '/app\n./data.csv (42 bytes)'}
    async def read_file(self,path): return self.files[path]
    async def write_file(self,path,data): self.files[path] = data; return len(data)
    async def usage(self,*args): pass
    async def log(self,*args): pass

@pytest.mark.asyncio
async def test_agent_writes_and_verifies(monkeypatch):
    monkeypatch.setenv('MODEL_NAME','claude-opus-5-5')
    session, model = FakeSession(), FakeModel()
    result = await solve(session,client=model)
    assert session.files['/app/out/report.md'] == b'Verified output'
    assert result == 'Verified /app/out/report.md: report exists.'
    assert len(model.calls) == 3
    assert any('QUALITY GATE' in str(m) for m in model.calls[2]['messages'])


def test_clip_and_compaction():
    assert 'omitted' in clip('x'*20000,1000)
    messages = [{'role':'system','content':'hi'}]
    messages += [{'role':'tool','content':'x'*3000} for _ in range(8)]
    assert compact(messages)
    assert any(len(m['content']) < 1000 for m in messages if m['role']=='tool')

class FakeMCPHost:
    mcp_servers = {'app':{'name':'app','url':'http://127.0.0.1:8000/mcp/'}}
    def __init__(self): self.requests = []
    async def http(self,url,body,headers,method='POST'):
        import base64
        request=json.loads(body)
        self.requests.append((request,headers))
        if request['method']=='initialize':
            value={'jsonrpc':'2.0','id':request['id'],'result':{'protocolVersion':'2025-03-26'}}
            hdr={'mcp-session-id':'test123'}
        elif request['method']=='tools/list':
            value={'jsonrpc':'2.0','id':request['id'],'result':{'tools':[{'name':'get','inputSchema':{'type':'object'}}]}}
            hdr={}
        elif request['method']=='tools/call':
            value={'jsonrpc':'2.0','id':request['id'],'result':{'content':[{'type':'text','text':'ok'}]}}
            hdr={}
        else:
            return {'status':202,'body_b64':''}
        return {'status':200,'headers':hdr,'body_b64':base64.b64encode(json.dumps(value).encode()).decode()}

@pytest.mark.asyncio
async def test_mcp_initialization_list_and_call():
    host=FakeMCPHost(); mcp=MCPBridge(host)
    assert (await mcp.list_tools('app'))[0]['name']=='get'
    assert (await mcp.call_tool('app','get',{}))['content'][0]['text']=='ok'
    assert len([x for x in host.requests if x[0]['method']=='initialize']) == 1
    assert host.requests[-1][1].get('Mcp-Session-Id')=='test123'

@pytest.mark.asyncio
async def test_agent_uses_only_declared_model(monkeypatch):
    monkeypatch.setenv('MODEL_NAME', 'claude-opus-5-5')
    monkeypatch.setattr('harness.VERIFY_GATE', False)
    session = FakeSession()
    model = FakeModel()
    result = await solve(session, client=model)
    assert '/app/out/report.md' in session.files
    assert all(c['model'] == 'claude-opus-5-5' for c in model.calls)

@pytest.mark.asyncio
async def test_mcp_tool_listing_requires_allowed_server():
    mcp = MCPBridge(FakeMCPHost())
    with pytest.raises(ValueError, match='Unknown MCP server'):
        await mcp.list_tools('some-other-server')
