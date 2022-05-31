import struct
import threading
import time

import zmq
from queue import Queue

car_pos = [9626, 9638, 9647, 9635, 10100, 10221, 10233, 10246]
car_speed = [11, 39, 25, 27, 15, 33, 8, 20]
car_way = [0, 1, 2, 3, 4, 5, 6, 7]
device_ip = [[192, 168, 1, 100], [192, 168, 1, 101]]
max_range = [[9616, 10256], [10257, 10897]]
car_num = "鄂A1V21{}       "
sn = 0


class MessageClient(object):
    def __init__(self, ip='localhost', port='8011'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.address = "tcp://{}:{}".format(ip, port)
        self.socket.connect(self.address)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
        self.q = Queue(maxsize=1000)
        self.is_re_build = True
        self.send_state = False
        self.Rebuild()
        self.bin_file = open('data.bin', 'ab')

    def SendThread(self):
        while True:
            time.sleep(0.05)
            msg = self.Dequeue()
            if msg is not None:
                try:
                    self.bin_file.write(msg)
                    rec = self.SendMsg(msg)
                    print(rec)
                except Exception as e:
                    print(e)

    def Rebuild(self):
        print('当前发送状态:' + str(self.send_state))
        print('发送缓冲区大小:' + str(self.q.qsize()))
        if self.is_re_build is False:
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poller.unregister(self.socket)
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.address)
            self.poller.register(self.socket, zmq.POLLIN)
            self.is_re_build = True
        threading.Timer(1.5, self.Rebuild).start()

    def SendMsg(self, msg):
        if self.is_re_build:
            self.socket.send(msg)
            if self.poller.poll(1000):
                resp = self.socket.recv()
                self.send_state = True
            else:
                self.is_re_build = False
                self.send_state = False
                raise Exception('Server no response.')
            return resp
        else:
            return None

    # def PackBag(self, dev_id, channel, sensor, value, min_s, max_s, c_type, count, timestamp):
    #     byte = struct.pack('iiiiiiiiQ', dev_id, channel, sensor, value, min_s, max_s, c_type, count, timestamp)
    #     self.Enqueue(byte)
    def PackBag(self):
        global car_pos
        global device_ip
        global car_num
        global max_range
        global sn
        num = [0, 0]
        pos = [[], []]
        for i in range(len(car_pos)):
            if car_pos[i] <= 10256:
                num[0] += 1
                pos[0].append([car_pos[i], car_num.format(str(i)), i])
            else:
                num[1] += 1
                pos[1].append([car_pos[i], car_num.format(str(i)), i])
            if i < 4:
                car_pos[i] += 11
                if car_pos[i] > 10887:
                    car_pos[i] = 9626
            else:
                car_pos[i] -= 11
                if car_pos[i] < 9626:
                    car_pos[i] = 10887
        for j in range(len(device_ip)):
            size = num[j]
            c_time = int(time.time() * 1000)
            device_b = struct.pack('BBBB', device_ip[j][0], device_ip[j][1], device_ip[j][2], device_ip[j][3])
            data_pack = struct.pack('i', sn) + device_b + struct.pack('qi', c_time, size)
            sn = sn + 1
            car_type = 1
            for z in range(num[j]):
                car_id = pos[j][z][2]
                car_plate = pos[j][z][1]
                car_range = [pos[j][z][0] - 10, pos[j][z][0] + 10]
                car_way = pos[j][z][2]
                car_edge = 0
                if car_id < 4:
                    car_direction = 0
                    if pos[j][z][0] + 11 > max_range[j][1]:
                        car_edge = 1
                else:
                    car_direction = 1
                    if pos[j][z][0] - 11 < max_range[j][0]:
                        car_edge = 1
                single_data = struct.pack('Q', car_id) + bytes(car_plate, encoding='utf8') + struct.pack('b', car_type)\
                    + struct.pack('IIf', car_range[0], car_range[1], 36.7) + struct.pack('b', car_way) + \
                    struct.pack('I', pos[j][z][0]) + struct.pack('bb', car_edge, car_direction)
                data_pack = data_pack + single_data
            self.Enqueue(data_pack)

    def Enqueue(self, block):
        # threadLock.acquire()
        if self.q.full():
            self.q.get()
        self.q.put(block)
        # threadLock.release()

    def Dequeue(self):
        # threadLock.acquire()
        if self.q.empty():
            return None
        else:
            return self.q.get()
        # threadLock.release()

if __name__ == '__main__':
    a = MessageClient()
    while True:
        time.sleep(0.2)
        try:
            data = a.SendMsg(b'ready')
            if data is not None:
                size = struct.unpack('i', data)
                print(size)
        except Exception as e:
            print(e)


