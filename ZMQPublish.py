import zmq
import time
import struct
import threading
from queue import Queue

# 两台方案模拟
car_pos = [9626, 9638, 9647, 9635, 10100, 10221, 10233, 10246]
car_speed = [6, 20, 12, 13, 7, 16, 4, 10]
car_way = [0, 0, 2, 3, 4, 6, 6, 7]
device_ip = [[192, 168, 1, 100], [192, 168, 1, 101]]
max_range = [[9616, 10256], [10257, 10897]]
car_num = "鄂A1V21{}       "
sn = [0, 0]


class MessagePublisher(object):
    def __init__(self, port='8030'):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:{}".format(port))
        self.q = Queue(maxsize=1000)
        self.bin_file = open('data.bin', 'ab')
        t = threading.Thread(target=self.SendThread, args=())
        t.setDaemon(True)
        t.start()

    def SendThread(self):
        while True:
            time.sleep(0.05)
            msg = self.Dequeue()
            if msg is not None:
                try:
                    # self.bin_file.write(msg)
                    self.socket.send(msg)
                except Exception as e:
                    print(e)

    def PackBag(self):
        global car_pos
        global device_ip
        global car_num
        global max_range
        global sn
        global car_speed
        global car_way
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
                car_pos[i] += car_speed[i]
                if car_pos[i] > 10887:
                    car_pos[i] = 9626
            else:
                car_pos[i] -= car_speed[i]
                if car_pos[i] < 9626:
                    car_pos[i] = 10887
            if abs(car_pos[0] - car_pos[1]) < 20:
                car_way[1] = 1
            else:
                if car_way[1] == 1:
                    car_way[1] = 0
            if abs(car_pos[5] - car_pos[6]) < 20:
                car_way[5] = 5
            else:
                if car_way[5] == 5:
                    car_way[5] = 6
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
                car_way_ = car_way[pos[j][z][2]]
                car_speed_ = car_speed[pos[j][z][2]]
                car_edge = 0
                if car_id < 4:
                    car_direction = 0
                    if pos[j][z][0] + car_speed_ > max_range[j][1] or pos[j][z][0] == 9626:
                        car_edge = 1
                else:
                    car_direction = 1
                    if pos[j][z][0] - car_speed_ < max_range[j][0] or pos[j][z][0] == 10887:
                        car_edge = 1
                single_data = struct.pack('Q', car_id) + bytes(car_plate, encoding='utf8') + struct.pack('b', car_type)\
                    + struct.pack('IIf', car_range[0], car_range[1], car_speed_ * 2) + struct.pack('b', car_way_) +\
                    struct.pack('I', pos[j][z][0]) + struct.pack('bb', car_edge, car_direction)
                data_pack = data_pack + single_data
            print('完成打包')
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
