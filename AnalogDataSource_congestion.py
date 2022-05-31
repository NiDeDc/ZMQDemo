import random
import struct
import time
from ZMQPublish_3 import MessagePublisher
import threading
import numpy as np
import config

# 两台协调器模拟
max_range = [1, 12398]  # 9616-10897， 10898-12398
car_pos = [[100,
            110,
            120,
            110,
            145,
            140,
            140],
           [random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1])]]
car_speed = [[1, 1, 1, 1,
              1,
              1,
              1],
             [7, 16, 4, 10,
              random.randint(4, 20),
              random.randint(4, 20),
              random.randint(4, 20),
              random.randint(4, 20)]]
car_id = [[1, 2, 3, 4, 9, 10, 11], [5, 6, 7, 8, 12, 13, 14, 15]]
car_way = [[1, 1, 3, 4,
            random.randint(1, 4),
            random.randint(1, 4),
            random.randint(1, 4)],
           [5, 7, 8, 8,
            random.randint(5, 8),
            random.randint(5, 8),
            random.randint(5, 8),
            random.randint(5, 8)]]
car_type = [[random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1)],
            [random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1),
             random.randint(0, 1)]]
device_ip = [[192, 168, 1, 100], [192, 168, 1, 101]]
car_num = "鄂A1V2{}       "
sn = [0, 0]

msg_1 = MessagePublisher(port=config.read_config('PORT', 'device1'))
msg_2 = MessagePublisher(port=config.read_config('PORT', 'device2'))
t_1 = threading.Thread(target=msg_1.SendThread, args=(), daemon=True)
t_2 = threading.Thread(target=msg_2.SendThread, args=(), daemon=True)


def GeneratedData():
    global car_pos
    global device_ip
    global car_num
    global max_range
    global sn
    global car_speed
    global car_way
    global car_id
    global car_type
    for i in range(len(car_pos)):
        cur_pos = car_pos[i]
        cur_speed = car_speed[i]
        cur_way = car_way[i]
        cur_sn = sn[i]
        cur_id = car_id[i]
        cur_type = car_type[i]
        for j in range(len(cur_pos)):
            if i == 0:
                cur_pos[j] += cur_speed[j]
                if cur_pos[j] > max_range[1]:
                    cur_pos[j] = max_range[0]
                else:
                    cur_pos[j] += cur_speed[j]
                    if cur_pos[j] > max_range[1]:
                        cur_pos[j] = max_range[0]
                    # if abs(cur_pos[0] - cur_pos[1]) < 20:
                    #     cur_way[1] = 1
                    # else:
                    #     if cur_way[1] == 1:
                    #         cur_way[1] = 0
            else:
                cur_pos[j] -= cur_speed[j]
                if cur_pos[j] < max_range[0]:
                    cur_pos[j] = max_range[1]
                # if abs(cur_pos[1] - cur_pos[2]) < 20:
                #     cur_way[1] = 5
                # else:
                #     if cur_way[1] == 5:
                #         cur_way[1] = 6
            a = np.array(cur_way)
            rep_num = np.where(a == cur_way[j])[0]
            for z in range(len(rep_num)):
                if j != rep_num[z]:
                    if abs(cur_pos[j] - cur_pos[rep_num[z]]) < 20:
                        if cur_way[j] != 4 and cur_way[j] != 8:
                            cur_way[j] += 1
                        else:
                            cur_way[j] -= 1
        size = len(car_pos[i])
        c_time = int(time.time() * 1000)
        device_b = struct.pack('BBBB', device_ip[i][0], device_ip[i][1], device_ip[i][2], device_ip[i][3])
        data_pack = struct.pack('i', cur_sn) + device_b + struct.pack('qi', c_time, size)
        cur_sn += 1
        for z in range(size):
            car_ids = cur_id[z]
            car_plate = car_num.format(car_ids)
            if len(car_plate) < 14:
                str_list = list(car_plate)
                str_list.insert(6, 'X')
                car_plate = ''.join(str_list)
            car_range = [cur_pos[z], cur_pos[z]]
            car_way_ = cur_way[z]
            if z == 2:
                if cur_pos[z] > 3000:
                    car_speed_ = 0
                else:
                    car_speed_ = cur_speed[z]
            else:
                car_speed_ = cur_speed[z]
            car_edge = 0
            car_position = cur_pos[z]
            if i == 0:
                car_direction = 0
                if cur_pos[z] + car_speed_ > max_range[1] or cur_pos[z] == 9626:
                    car_edge = 1
            else:
                car_direction = 1
                if cur_pos[z] - car_speed_ < max_range[0] or cur_pos[z] == 12388:
                    car_edge = 1
            single_data = struct.pack('Q', car_ids) + bytes(car_plate, encoding='utf8') + struct.pack('b', cur_type[z]) \
                          + struct.pack('IIf', car_range[0], car_range[1], car_speed_ * 2) + struct.pack('b',
                                                                                                         car_way_) + \
                          struct.pack('I', car_position) + struct.pack('bb', car_edge, car_direction)
            data_pack = data_pack + single_data
        # print('完成打包')
        if i == 0:
            msg_1.Enqueue(data_pack)
            print('协调器1发送')
        else:
            msg_2.Enqueue(data_pack)
            print('协调器2发送')


if __name__ == '__main__':
    t_1.start()
    t_2.start()
    while True:
        GeneratedData()
        time.sleep(0.5)
