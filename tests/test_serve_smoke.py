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
