import datetime
import time
import zmq
import struct
import numpy as np
from queue import Queue
import threading

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:8011")
q = Queue(maxsize=1000)
# threadLock = threading.Lock()


def Enqueue(block):
    # threadLock.acquire()
    if q.full():
        q.get()
    q.put(block)
    # threadLock.release()


def Dequeue():
    # threadLock.acquire()
    if q.empty():
        return None
    else:
        return q.get()
    # threadLock.release()


def ReceiveData():
    while True:
        #  Wait for next request from client
        message = socket.recv()
        print("Received request: %s" % message)
        # 'hhiiq'
        # shell = message[0:20]
        # head_length = struct.calcsize('hhii')
        # head = struct.unpack_from('hhii', shell, 0)
        # datatime = struct.unpack_from("Q", shell, head_length)[0]
        # data = np.frombuffer(message[20:], dtype=np.float32)
        # sample = head[3] // head[2]
        # data = data.reshape(sample, head[2])
        # # timeStamp = datetime.datetime.fromtimestamp(datatime / 1000)
        # # time_string = timeStamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        # t_data = [head[0], head[1], datatime, data]
        # Enqueue(t_data)

        #  Send reply back to client
        socket.send(b"ok")

if __name__ == '__main__':
        t = threading.Thread(target=ReceiveData, args=())
        t.setDaemon(True)
        t.start()
        while True:
            time.sleep(1)