import asyncio
import base64
import json
import pytest
import websockets
import serve

@pytest.mark.asyncio
async def test_server_completes_real_websocket_protocol(monkeypatch):
    async def demo_solver(session):
        result=await session.exec('pwd',10)
        assert result['output']=='/app'
        await session.write_file('/app/out.txt',b'smoke pass')
        return 'Wrote /app/out.txt'
    monkeypatch.setattr(serve,'solve',demo_solver)
    async with websockets.serve(serve.handle,'127.0.0.1',0,ping_interval=None) as server:
        port=server.sockets[0].getsockname()[1]
        async with websockets.connect(f'ws://127.0.0.1:{port}') as ws:
            await ws.send(json.dumps({'type':'task','protocol':1,'instruction':'smoke','workdir':'/app','limits':{'agent_timeout_sec':60}}))
            seen=[]
            while True:
                item=json.loads(await asyncio.wait_for(ws.recv(),timeout=5)); seen.append(item)
                if item['type']=='exec':
                    await ws.send(json.dumps({'type':'result','id':item['id'],'exit_code':0,'output':'/app'}))
                if item['type']=='write_file':
                    assert base64.b64decode(item['content_b64'])==b'smoke pass'
                    await ws.send(json.dumps({'type':'result','id':item['id'],'ok':True,'size':10}))
                if item['type']=='done':
                    assert '/app/out.txt' in item['final_message']
                    break
            assert any(x['type']=='write_file' for x in seen)


@pytest.mark.asyncio
async def test_complete_websocket_agent_loop_with_stubbed_model(monkeypatch):
    """Run the real solve() over WebSocket on a short task without paid model calls."""
    from types import SimpleNamespace
    import harness

    class FakeMessage:
        def __init__(self, content=None, tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls or []
        def model_dump(self, exclude_none=True):
            data = {'role':'assistant', 'content':self.content}
            if self.tool_calls:
                data['tool_calls'] = [
                    {'id':call.id, 'type':'function', 'function':{
                        'name':call.function.name,
                        'arguments':call.function.arguments}}
                    for call in self.tool_calls]
            return data

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.count=0
            self.chat=SimpleNamespace(completions=SimpleNamespace(create=self.create))
        async def create(self, **kwargs):
            self.count += 1
            if self.count == 1:
                call=SimpleNamespace(id='write', function=SimpleNamespace(
                    name='write_file', arguments=json.dumps({
                        'path':'/app/summary.md','content':'Engineering memo'})))
                message=FakeMessage(tool_calls=[call])
            elif self.count == 2:
                message=FakeMessage(content='Wrote draft')
            else:
                message=FakeMessage(content='Verified /app/summary.md')
            return SimpleNamespace(usage=None,choices=[
                SimpleNamespace(message=message,finish_reason='stop')])
        async def close(self):
            pass

    monkeypatch.setenv('MODEL_NAME','claude-opus-5-5')
    monkeypatch.setattr(harness.openai,'AsyncOpenAI',FakeClient)
    async with websockets.serve(serve.handle,'127.0.0.1',0,ping_interval=None) as server:
        port=server.sockets[0].getsockname()[1]
        async with websockets.connect(f'ws://127.0.0.1:{port}') as ws:
            await ws.send(json.dumps({'type':'task','protocol':1,
                'instruction':'Create /app/summary.md','workdir':'/app',
                'limits':{'agent_timeout_sec':90,'exec_timeout_sec':60}}))
            writes=[]
            while True:
                frame=json.loads(await asyncio.wait_for(ws.recv(),timeout=5))
                if frame['type']=='exec':
                    await ws.send(json.dumps({'type':'result','id':frame['id'],
                        'exit_code':0,'output':'/app/summary.md (16 bytes)'}))
                elif frame['type']=='write_file':
                    writes.append((frame['path'],base64.b64decode(frame['content_b64'])))
                    await ws.send(json.dumps({'type':'result','id':frame['id'],
                        'ok':True,'size':len(writes[-1][1])}))
                elif frame['type']=='done':
                    assert 'Verified /app/summary.md' in frame['final_message']
                    break
                elif frame['type']=='error':
                    pytest.fail(frame['message'])
            assert writes == [('/app/summary.md',b'Engineering memo')]

@pytest.mark.asyncio
async def test_cancel_during_model_request_returns_done_promptly(monkeypatch):
    """PLE's cancellation grace period must not be spent awaiting a slow model."""
    from types import SimpleNamespace
    import harness

    model_started = asyncio.Event()

    class SlowModel:
        def __init__(self, *a, **kw):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

        async def create(self, **kw):
            model_started.set()
            await asyncio.sleep(120)
            raise AssertionError('Cancelled model call should not finish')

        async def close(self):
            pass

    monkeypatch.setenv('MODEL_NAME', 'claude-opus-5-5')
    monkeypatch.setattr(harness.openai, 'AsyncOpenAI', SlowModel)

    async with websockets.serve(serve.handle, '127.0.0.1', 0, ping_interval=None) as server:
        port = server.sockets[0].getsockname()[1]
        async with websockets.connect(f'ws://127.0.0.1:{port}') as ws:
            await ws.send(json.dumps({
                'type':'task', 'protocol':1, 'instruction':'Build an engineering memo',
                'workdir':'/app', 'limits':{'agent_timeout_sec':120}
            }))
            frame = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
            assert frame['type'] == 'exec'
            await ws.send(json.dumps({
                'type':'result', 'id':frame['id'], 'exit_code':0,
                'output':'/app',
            }))
            await asyncio.wait_for(model_started.wait(), timeout=3)
            await ws.send(json.dumps({'type':'cancel', 'reason':'timeout'}))
            final = json.loads(await asyncio.wait_for(ws.recv(), timeout=2))
            assert final['type'] == 'done'
            assert isinstance(final['final_message'], str)
