"""PLE WebSocket protocol v1 client: isolated per-task request/response dispatcher.

Original code, following https://github.com/google-research/ple/blob/main/docs/protocol.md
"""
from __future__ import annotations
import asyncio
import base64
import itertools
import json
import time
from typing import Any

MAX_FRAME = 16 * 1024 * 1024
MAX_WRITE = 9_000_000

class TaskCancelled(Exception):
    pass

class TaskFailure(Exception):
    pass

class Session:
    def __init__(self, ws: Any, task: dict[str, Any]):
        self.ws, self.task = ws, task
        self.instruction = task['instruction']
        self.workdir = task.get('workdir') or '/'
        self.mcp_servers = {s['name']: s for s in task.get('mcp_servers', []) if isinstance(s, dict) and s.get('name') and s.get('url')}
        self.limits = task.get('limits') or {}
        duration = self.limits.get('agent_timeout_sec')
        self.deadline = time.monotonic() + float(duration) if isinstance(duration, (int,float)) and duration > 0 else None
        self.pending: dict[str, asyncio.Future] = {}
        self.counter = itertools.count(1)
        self.lock = asyncio.Lock()
        self.cancelled = asyncio.Event()
        self.last_summary = 'No model summary was produced.'

    def time_left(self) -> float | None:
        return self.deadline - time.monotonic() if self.deadline else None

    async def send(self, frame: dict[str, Any]):
        async with self.lock:
            await self.ws.send(json.dumps(frame, ensure_ascii=False))

    async def reader(self):
        try:
            async for raw in self.ws:
                try:
                    msg = json.loads(raw)
                except (TypeError, ValueError):
                    continue
                if not isinstance(msg, dict):
                    continue
                if msg.get('type') == 'cancel':
                    self.cancelled.set()
                    break
                if msg.get('type') == 'result':
                    fut = self.pending.pop(str(msg.get('id')), None)
                    if fut and not fut.done():
                        fut.set_result(msg)
        finally:
            self.cancelled.set()
            for fut in self.pending.values():
                if not fut.done():
                    fut.set_exception(TaskCancelled('Task cancelled or connection closed'))
            self.pending.clear()

    async def request(self, kind: str, **kwargs) -> dict[str, Any]:
        if self.cancelled.is_set():
            raise TaskCancelled('Task cancelled')
        rid = str(next(self.counter))
        future = asyncio.get_running_loop().create_future()
        self.pending[rid] = future
        try:
            await self.send({'type': kind, 'id': rid, **kwargs})
            # Allow long operations without ping disconnects; honor overall deadline.
            timeout = self.time_left()
            result = await asyncio.wait_for(future, timeout=max(1.0, timeout) if timeout is not None else 640.0)
            if result.get('ok') is False:
                raise TaskFailure(str(result.get('error', 'Unknown evaluator error')))
            return result
        finally:
            self.pending.pop(rid, None)

    async def exec(self, command: str, timeout: int = 120):
        limit = self.limits.get('exec_timeout_sec') or 600
        return await self.request('exec', command=command, timeout_sec=min(max(1, int(timeout)), int(limit), 600))

    async def read_file(self, path: str) -> bytes:
        r = await self.request('read_file', path=path)
        if r.get('truncated'):
            raise TaskFailure(f'File {path} larger than max readable payload; use bash to read slices')
        return base64.b64decode(r.get('content_b64', ''))

    async def write_file(self, path: str, data: bytes) -> int:
        if not isinstance(data, bytes):
            raise TypeError('write_file content must be bytes')
        if len(data) == 0:
            await self.request('write_file', path=path, content_b64='', append=False)
            return 0
        count = 0
        for i in range(0, len(data), MAX_WRITE):
            chunk = data[i:i+MAX_WRITE]
            await self.request('write_file', path=path, content_b64=base64.b64encode(chunk).decode(), append=i != 0)
            count += len(chunk)
        return count

    async def http(self, url: str, body: bytes, headers: dict[str, str], method: str = 'POST'):
        if not any(url == s['url'] or url.startswith(s['url'].rstrip('/') + '/') for s in self.mcp_servers.values()):
            raise ValueError('HTTP request is not to an approved task MCP server')
        return await self.request('http', method=method, url=url, headers=headers, body_b64=base64.b64encode(body).decode(), timeout_sec=120)

    async def log(self, message: str):
        await self.send({'type': 'log', 'text': str(message)[:1000]})

    async def usage(self, model: str, prompt: int, completion: int, cached: int = 0):
        await self.send({'type': 'usage', 'model': model,
                         'input_tokens': max(0, int(prompt)), 'output_tokens': max(0, int(completion)),
                         'cache_read_tokens': max(0, int(cached))})
