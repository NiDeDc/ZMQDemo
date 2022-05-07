# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 按两次 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import time
import struct

import ZMQServer
import threading
from ZMQClient import MessageClient
from ZMQPublish_3 import MessagePublisher
# import FileControl


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')
    # FileControl
    msg = MessagePublisher(port='8030')
    t = threading.Thread(target=msg.SendThread, args=())
    t.setDaemon(True)
    t.start()
    # data = ReadCSV.bin_data
    while True:
        msg.PackBag()
        time.sleep(0.5)
        # for i in data:
        #     msg.Enqueue(i)
        #     print('完成发送')
        #     time.sleep(0.25)
        # time.sleep(3)



# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
