"""MCP Streamable-HTTP tool discovery/calls through the evaluator's task-container relay."""
from __future__ import annotations
import base64
import itertools
import json
from typing import Any

class MCPBridge:
    def __init__(self, session):
        self.session = session
        self.state: dict[str, dict[str, str]] = {}
        self.reqids = itertools.count(1)

    async def rpc(self, name: str, method: str, params: dict[str, Any] | None = None):
        server = self.session.mcp_servers.get(name)
        if not server:
            raise ValueError(f'Unknown MCP server {name!r}, available: {list(self.session.mcp_servers)}')
        state = self.state.setdefault(name, {})
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
        if state.get('session_id'):
            headers['Mcp-Session-Id'] = state['session_id']
        if state.get('version'):
            headers['MCP-Protocol-Version'] = state['version']
        frame = {'jsonrpc': '2.0', 'id': next(self.reqids), 'method': method}
        if params is not None:
            frame['params'] = params
        response = await self.session.http(server['url'], json.dumps(frame).encode(), headers)
        response_headers = {k.lower(): v for k,v in (response.get('headers') or {}).items()}
        if response_headers.get('mcp-session-id'):
            state['session_id'] = response_headers['mcp-session-id']
        body = base64.b64decode(response.get('body_b64') or '')
        if response.get('status', 200) >= 400:
            raise RuntimeError(f'MCP {method}: HTTP {response.get("status")}: {body[:700]!r}')
        text = body.decode('utf-8', 'replace')
        # Streamable HTTP may use SSE, with one or more data: JSON-RPC frames.
        if text.lstrip().startswith('data:') or 'event: message' in text:
            packets = []
            for line in text.splitlines():
                if line.startswith('data:'):
                    try: packets.append(json.loads(line[5:].strip()))
                    except json.JSONDecodeError: pass
            result = next((p for p in reversed(packets) if 'result' in p or 'error' in p), {})
        else:
            result = json.loads(text or '{}') if text else {}
        if result.get('error'):
            raise RuntimeError(f'MCP {method}: {result["error"]}')
        return result.get('result', {})

    async def initialize(self, name: str):
        if name in self.state and self.state[name].get('initialized'):
            return
        payload = {'protocolVersion': '2025-03-26', 'capabilities': {},
                   'clientInfo': {'name': 'aegis-ple', 'version': '0.1.0'}}
        response = await self.rpc(name, 'initialize', payload)
        self.state[name]['version'] = response.get('protocolVersion', '2025-03-26')
        server = self.session.mcp_servers[name]
        state = self.state[name]
        headers = {'Content-Type':'application/json','Accept':'application/json, text/event-stream',
                   'MCP-Protocol-Version': state['version']}
        if state.get('session_id'):
            headers['Mcp-Session-Id'] = state['session_id']
        notification = {'jsonrpc': '2.0', 'method': 'notifications/initialized'}
        await self.session.http(server['url'], json.dumps(notification).encode(), headers)
        self.state[name]['initialized'] = '1'

    async def list_tools(self, name: str):
        await self.initialize(name)
        # MCP pagination; limit context instead of silently hiding tool definitions.
        result, tools, cursor = {}, [], None
        for _ in range(15):
            result = await self.rpc(name, 'tools/list', {'cursor': cursor} if cursor else {})
            tools += result.get('tools', [])
            cursor = result.get('nextCursor')
            if not cursor: break
        return tools

    async def call_tool(self, name: str, tool: str, arguments: dict[str, Any]):
        await self.initialize(name)
        return await self.rpc(name, 'tools/call', {'name': tool, 'arguments': arguments})
