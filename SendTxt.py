import time
from ReadTxt import *
import ReadTxt
import struct
from ZMQPublish import MessagePublisher

bin_data = []
bin_file = open('data5_7.bin', 'ab')
AllData = ReadTxt.AllData
a = MessagePublisher()
for i in range(len(AllData)):
    curData: frameData = AllData[i]
    data_pack = struct.pack('i4Bqi', curData.sn, curData.ip[0], curData.ip[1], curData.ip[2], curData.ip[3], curData.timestamp, curData.num)
    for j in range(len(curData.CarData)):
        curCar: CarData = curData.CarData[j]
        single_data = struct.pack('Q', curCar.id) + bytes(curCar.plate, encoding='utf8') + \
                      struct.pack('b', curCar.type) + \
                      struct.pack('IIf', curCar.range[0], curCar.range[1], curCar.speed) + \
                      struct.pack('b', curCar.lane) + struct.pack('I', curCar.position) + \
                      struct.pack('bb', curCar.edge, curCar.direction)
        data_pack += single_data
    bin_file.write(data_pack)
    bin_data.append(data_pack)
    a.Enqueue(data_pack)
    time.sleep(0.5)
bin_file.close()


