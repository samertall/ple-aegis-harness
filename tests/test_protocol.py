import asyncio
import base64
import json
import pytest
from protocol import Session

class MockWebSocket:
    def __init__(self): self.queue=asyncio.Queue(); self.frames=[]
    async def send(self,raw):
        msg=json.loads(raw); self.frames.append(msg)
        if msg['type']=='exec':
            await self.queue.put(json.dumps({'type':'result','id':msg['id'],'exit_code':0,'output':'ok'}))
        if msg['type']=='write_file':
            await self.queue.put(json.dumps({'type':'result','id':msg['id'],'ok':True,'size':8}))
        if msg['type']=='read_file':
            await self.queue.put(json.dumps({'type':'result','id':msg['id'],'ok':True,'content_b64':base64.b64encode(b'hello').decode(),'size':5}))
    def __aiter__(self): return self
    async def __anext__(self):
        result=await self.queue.get()
        if result is None: raise StopAsyncIteration
        return result

@pytest.mark.asyncio
async def test_protocol_roundtrip():
    ws=MockWebSocket()
    s=Session(ws,{'instruction':'test','workdir':'/app','limits':{'agent_timeout_sec':100,'exec_timeout_sec':600}})
    reader=asyncio.create_task(s.reader())
    try:
        assert (await s.exec('ls'))['output']=='ok'
        assert await s.read_file('file.txt')==b'hello'
        assert await s.write_file('out.txt',b'content')==7
        assert any(f['type']=='write_file' and f.get('append') is False for f in ws.frames)
    finally:
        await ws.queue.put(None)
        await reader

@pytest.mark.asyncio
async def test_protocol_rejects_failed_file_read():
    class FailedRead(MockWebSocket):
        async def send(self, raw):
            msg = json.loads(raw)
            self.frames.append(msg)
            if msg['type'] == 'read_file':
                await self.queue.put(json.dumps({'type': 'result', 'id': msg['id'], 'ok': False, 'error': 'not found'}))

    from protocol import TaskFailure
    ws = FailedRead()
    s = Session(ws, {'instruction': 'test'})
    reader = asyncio.create_task(s.reader())
    try:
        with pytest.raises(TaskFailure, match='not found'):
            await s.read_file('/missing.txt')
    finally:
        await ws.queue.put(None)
        await reader

@pytest.mark.asyncio
async def test_protocol_write_chunking(monkeypatch):
    import protocol
    monkeypatch.setattr(protocol, 'MAX_WRITE', 4)
    ws = MockWebSocket()
    s = Session(ws, {'instruction': 'test'})
    reader = asyncio.create_task(s.reader())
    try:
        assert await s.write_file('chunk.txt', b'abcdefghij') == 10
        chunks = [f for f in ws.frames if f['type'] == 'write_file']
        assert [c['append'] for c in chunks] == [False, True, True]
        assert b''.join(base64.b64decode(c['content_b64']) for c in chunks) == b'abcdefghij'
    finally:
        await ws.queue.put(None)
        await reader
