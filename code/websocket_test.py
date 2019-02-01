import websocket
import queue
import threading


def on_message(ws, msg):
    qq.put(msg)


def qget(q):
    while True:
        print(q.get())


def wsrun():
    ws.run_forever()


qq = queue.Queue(maxsize=100)
ws = websocket.WebSocketApp('ws://stream.meetup.com/2/rsvps',
                            on_message=on_message)

t1 = threading.Thread(target=wsrun, args=())
t2 = threading.Thread(target=qget, args=(qq,))

t1.start()
t2.start()

t1.join()
t2.join()
