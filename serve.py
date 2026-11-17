"""Standalone WebSocket serve entrypoint for PLE v1."""
from __future__ import annotations
import asyncio
import json
import logging
import os
import websockets
from protocol import Session, TaskCancelled
from harness import solve

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper())
log = logging.getLogger('aegis')

async def handle(ws):
    try:
        payload = json.loads(await ws.recv())
        if payload.get('type') != 'task' or payload.get('protocol') != 1:
            await ws.send(json.dumps({'type':'error','message':'Expected PLE task protocol v1'}))
            return
        session = Session(ws, payload)
        listener = asyncio.create_task(session.reader())
        try:
            summary = await solve(session)
            await session.send({'type':'done', 'final_message': str(summary or session.last_summary)[:500_000]})
        except TaskCancelled:
            # The evaluator only grants a brief post-cancellation grace period.
            try:
                await session.send({'type':'done', 'final_message':
                                    session.last_summary[:500_000]})
            except Exception:
                pass
        except Exception as e:
            log.exception('Agent failed')
            # Graceful completion allows grading of whatever was written.
            try:
                await session.log(f'Agent exception {type(e).__name__}: {str(e)[:250]}')
                await session.send({'type':'done','final_message': session.last_summary[:500_000]})
            except Exception:
                pass
        finally:
            listener.cancel()
            await asyncio.gather(listener, return_exceptions=True)
    except Exception:
        log.exception('Protocol-level failure')
        try: await ws.send(json.dumps({'type':'error','message':'Unable to start task'}))
        except Exception: pass

async def main():
    port = int(os.getenv('PORT', '8765'))
    async with websockets.serve(handle, '0.0.0.0', port, ping_interval=None,
                                max_size=16*1024*1024, compression=None):
        log.info('Aegis PLE listening on %s',port)
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
