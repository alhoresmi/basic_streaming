"""
non asyncio example
"""


import websocket
import queue
import threading
import json
import toolz


def on_message(ws, msg):
    qq.put(msg)


def qget(q):
    while True:
        yield q.get()


def process_msg(q):
    return toolz.thread_last(qget(q),
                      (map, json.loads),
                      (map, lambda v: v['event']),
                      (filter, lambda v: str_filter(v['event_name'])))


def str_filter(s):
    return 'machine learning' in s.lower()


def show_stream(q):
    for v in process_msg(q):
        print(v)


def wsrun():
    ws.run_forever()


qq = queue.Queue(maxsize=100)
ws = websocket.WebSocketApp('ws://stream.meetup.com/2/rsvps',
                            on_message=on_message)

t1 = threading.Thread(target=wsrun, args=())
t2 = threading.Thread(target=show_stream, args=(qq,))

t1.start()
t2.start()

t1.join()
t2.join()
