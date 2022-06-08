import random
import struct
import time
from ZMQPublish_3 import MessagePublisher
import threading
import numpy as np
import config

# 两台协调器模拟
leavePos = [
    [[4418, 4563], [12485, 13130]],
    [[5114.3, 5644.3]]
]
comePos = [
    [[4514.3, 5419.3], [4594.5, 4874.5]],
    [[4348, 4848], [12060, 12850]]
]
max_range = [3600, 12676]  # 9616-10897， 10898-12398
car_pos = [[random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1])],
           [random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1]),
            random.randint(max_range[0], max_range[1])]]
car_speed = [[6, 20, 12, 13,
              random.randint(4, 20),
              random.randint(4, 20),
              random.randint(4, 20)],
             [7, 16, 4, 10,
              random.randint(4, 20),
              random.randint(4, 20),
              random.randint(4, 20),
              random.randint(4, 20)]]
# car_id = [[1, 2, 3, 4, 9, 10, 11], [5, 6, 7, 8, 12, 13, 14, 15]]
car_id = [[1, 2, 3, 4, 9, 10, 11], [1, 2, 3, 4, 9, 10, 11, 15]]
car_way = [[0, 0, 0, 0,
            random.randint(0, 3),
            random.randint(0, 3),
            random.randint(0, 3)],
           [0,
            0,
            0,
            0,
            random.randint(0, 3),
            random.randint(0, 3),
            random.randint(0, 3),
            random.randint(0, 3)]]
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
    global leavePos
    global car_pos
    global device_ip
    global car_num
    global max_range
    global sn
    global car_speed
    global car_way
    global car_id
    global car_type
    delete_index = []
    for i in range(len(car_pos)):
        for j in range(len(car_pos[i])):
            if car_way[i][j] == 4:
                delete_index.append([i, j])
    for d in delete_index:
        deleteCar(index1=d[0], index2=d[1])
    for i in range(len(car_pos)):
        cur_pos = car_pos[i]
        cur_speed = car_speed[i]
        cur_way = car_way[i]
        cur_sn = sn[i]
        cur_id = car_id[i]
        cur_type = car_type[i]
        cur_leave = leavePos[i]
        for j in range(len(cur_pos)):
            if i == 0:
                cur_pos[j] += cur_speed[j]
                if cur_pos[j] > 12676:
                    cur_pos[j] = 3600
            else:
                cur_pos[j] -= cur_speed[j]
                if cur_pos[j] < 3600:
                    cur_pos[j] = 12676
            for k in range(len(cur_leave)):
                if cur_leave[k][0] < cur_pos[j] < cur_leave[k][1] and cur_way[j] == 0:
                    cur_way[j] = 4
            way_array = np.array(cur_way)
            rep_num = np.where(way_array == cur_way[j])[0]
            for z in range(len(rep_num)):
                if j != rep_num[z]:
                    if abs(cur_pos[j] - cur_pos[rep_num[z]]) < 20:
                        if cur_way[j] < 4:
                            if cur_way[j] != 0:
                                cur_way[j] -= 1
                            else:
                                cur_way[j] += 1
        size = len(car_pos[i])
        c_time = int(time.time() * 1000)
        device_b = struct.pack('4B', device_ip[i][0], device_ip[i][1], device_ip[i][2], device_ip[i][3])
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
            if cur_way[z] == 0:
                car_way_ = 9
            elif cur_way[z] < 4:
                car_way_ = 4 - cur_way[z]
            else:
                car_way_ = cur_way[z]
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
        else:
            msg_2.Enqueue(data_pack)


def deleteCar(index1, index2):
    global car_pos
    global car_speed
    global car_way
    global car_id
    global car_type
    print("car id ", car_id[index1][index2], "leave")
    del car_pos[index1][index2]
    del car_speed[index1][index2]
    del car_way[index1][index2]
    del car_id[index1][index2]
    del car_type[index1][index2]


if __name__ == '__main__':
    t_1.start()
    t_2.start()
    while True:
        GeneratedData()
        time.sleep(0.5)
