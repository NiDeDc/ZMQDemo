import csv
import struct


class CarData:
    def __init__(self):
        self.id = 0
        self.plate = '鄂A1V21A       '
        self.type = 0
        self.scope = [0, 0]
        self.speed = 0.0
        self.way = 0
        self.mil = 0
        self.edge = 0
        self.direction = 0


class SingleFrameData:
    def __init__(self):
        self.sn = 0
        self.ip = [192, 168, 1, 100]
        self.timestamp = 0
        self.car_size = 0
        self.carData = []

    def AppendCarData(self, data: CarData):
        self.carData.append(data)


filename = 'data4_27.csv'
bin_data = []
record = []
with open(filename) as f:
    reader = csv.reader(f)
    for row in reader:
        one = SingleFrameData()
        row[0:7] = map(int, row[0:7])
        one.sn = row[0]
        one.timestamp = row[5]
        one.car_size = row[6]
        data_pack = struct.pack('i4Bqi', row[0], row[1], row[2], row[3], row[4], row[5], row[6])
        if row[6] > 0:
            for i in range(7, 7 + row[6]):
                car_data = row[i][1:-1].split(',')
                car_data[2:5] = map(int, car_data[2:5])
                car_data[6:10] = map(int, car_data[6:10])
                one_car_data = CarData()
                one_car_data.id = int(car_data[0])
                one_car_data.type = car_data[2]
                one_car_data.scope[0] = car_data[3]
                one_car_data.scope[1] = car_data[4]
                one_car_data.speed = float(car_data[5])
                one_car_data.way = car_data[6]
                one_car_data.mil = car_data[7]
                one_car_data.edge = car_data[8]
                one_car_data.direction = car_data[9]
                one.carData.append(one_car_data)
                # cc = car_data[1][2:-1]
                # pp = bytes(car_data[1][2:-1], encoding='utf8')
                single_data = struct.pack('Q', int(car_data[0])) + bytes(car_data[1][2:-1],
                                                                         encoding='utf8') + struct.pack('b',
                                                                                                        car_data[2]) + \
                              struct.pack('IIf', car_data[3], car_data[4], float(car_data[5])) + \
                              struct.pack('b', car_data[6]) + struct.pack('I', car_data[7]) + \
                              struct.pack('bb', car_data[8], car_data[9])
                data_pack += single_data
        bin_data.append(data_pack)
        record.append(one)
new_record = []
size = len(record)
for i in range(size):
    if i != size - 1:
        new_record.append(record[i])
        new_one = SingleFrameData()
        new_one.sn = record[i].sn + 1
        new_one.timestamp = (record[i].timestamp + record[i+1].timestamp) // 2
        new_one.car_size = min(record[i].car_size, record[i+1].car_size)
        record[i+1].sn = new_one.sn + 1
        for j in range(len(record[i].carData)):
            curData: CarData = record[i].carData[j]
            nextData: CarData = CarData()
            for iterator in record[i+1].carData:
                if curData.id == iterator.id:
                    nextData = iterator
            if curData.id == nextData.id:
                interData = CarData()
                interData.id = curData.id
                interData.type = curData.type
                interData.scope[0] = (curData.scope[0] + nextData.scope[0]) // 2
                interData.scope[1] = (curData.scope[1] + nextData.scope[1]) // 2
                interData.speed = (curData.speed + nextData.speed) / 2
                interData.way = curData.way
                interData.mil = (curData.mil + nextData.mil) // 2
                interData.edge = curData.edge
                interData.direction = curData.direction
                new_one.carData.append(interData)
        new_record.append(new_one)
    else:
        pass
# new_filename = 'interData.csv'
# with open(new_filename, 'w', newline='') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter=',')
#     for i in range(len(new_record)):
#         curFrame: SingleFrameData = new_record[i]
#         pp = [curFrame.sn, curFrame.ip[0], curFrame.ip[1], curFrame.ip[2], curFrame.ip[3], curFrame.timestamp,
#               curFrame.car_size]
#         for j in range(len(curFrame.carData)):
#             curCar: CarData = curFrame.carData[j]
#             pp.append([curCar.id, curCar.plate, curCar.type, curCar.scope[0], curCar.scope[1], curCar.speed,
#                        curCar.way, curCar.mil, curCar.edge, curCar.direction])
#         csvwriter.writerow(pp)
kk = 5
