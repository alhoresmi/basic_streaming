"""
    This script will work with stream of json data from ws://stream.meetup.com/2/rsvps
    in asynchronous manner. one coroutine will get data from socket and put ig to queue
    another one will get data from queue

    Important: python 3.7 needed

    TODO:
    1. put data from queue to MQ or database
    2. refactor gags. better understanding of asyncio needed
"""


import asyncio
import aiohttp
import queue
import json


async def aws_read(q, n=-1):
    """
        Code example to work with websocket:
            https://aiohttp.readthedocs.io/en/stable/client_quickstart.html#aiohttp-client-websockets
        Idea to work with meetup rsvp API from:
            Psaltis Understanding the real-time pipeline
        meetup streaming api via websocket:
            https://www.meetup.com/meetup_api/docs/stream/2/rsvps/#websockets
    """
    cnt = 0
    host = 'ws://stream.meetup.com/2/rsvps'
    session = aiohttp.ClientSession()
    async with session.ws_connect(host) as ws:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close cmd':
                    await ws.close()
                    break
                else:
                    if (cnt > n) & (n != -1):
                        await session.close()
                        break
                    q.put(json.loads(msg.data))
                    cnt += 1
                    await ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break


async def qget(q):
    """
        Read data from queue. Stop if queue is empty for some tangible time inteval
    """
    cnt_miss = 0
    while True:
        # Caution! GAGs
        if cnt_miss > 200:
            break
        if q.empty():
            cnt_miss += 1
            await asyncio.sleep(.1)
        else:
            q.get()


async def main(q):
    tasks = []
    for c in [aws_read(q, 20), qget(q)]:
        task = asyncio.ensure_future(c)
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == '__main__':
    qq = queue.Queue(maxsize=1000)

    asyncio.get_event_loop().run_until_complete(main(qq))