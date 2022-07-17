"""
本脚本用于测出csgo的实际移动和输入的鼠标移动量的关系
游戏内鼠标加速 取1 开镜加速取 0.83 Tune选择2.4 巨准
上一条属于华电脑的参数，幼女控请另调，参照29行注释
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
import win32gui
import sys
import pydirectinput
import cv2
import numpy as np
import keyboard
import torch
import os
import time

ScreenX = 2560
ScreenY = 1600
CX = ScreenX // 2
CY = ScreenY // 2
ShotW = 2560
ShotH = 1600
Tune = 2.4
"""
重新调Tune:
    先将上面的Tune置为1
    游戏内鼠标加速建议设为一个整数，1或者2，开镜的加速值设为1
    游戏内多按几次x看一下推荐的Tune，自己估一个差不多的数
    改成那个Tune后调开镜参数

    游戏内开镜按x，也是自己选一个差不多的平均数
    然后把游戏内的开镜加速参数设成这个新推荐的Tune
"""

def QImageToCvMat(incomingImage):
    '''  Converts a QImage into an opencv MAT format  '''
    incomingImage = incomingImage.convertToFormat(QImage.Format.Format_RGBA8888)
    width = incomingImage.width()
    height = incomingImage.height()
    ptr = incomingImage.bits()
    ptr.setsize(height * width * 4)
    arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
    return arr.copy()

def calc_head(p):
    #print(p)
    head_x = int((p['xmin'] + p['xmax']) // 2)
    head_y = int(p['ymin'] + (p['xmax'] - p['xmin']) / 4)
    dis = abs(head_x - ScreenX // 2) + abs(head_y - ScreenY // 2)
    
    if p['xmin'] > 1200 and p['xmax'] > 1550 and p['ymin'] < 1400 and p['ymax'] > 1550:
        head_x = -1
        head_y = -1
        dis = 1e5
    return ((head_x, head_y), dis)


pydirectinput.PAUSE = 0
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
# model = torch.hub.load('ultralytics/yolov5', 'custom', 'C:\\Users\\HH\\iCloudDrive\\Classes\\AI001\\FPSAutomaticAiming-main\\yolov5s.pt')
# model = torch.hub.load('ultralytics/yolov5', 'custom', 'C:\\Users\\HH\\iCloudDrive\\Classes\\AI001\\FPSAutomaticAiming-main\\runs\\train\\exp\\weights\\best.pt')
# model = torch.hub.load('ultralytics/yolov5', 'yolov5n').to(device)
file_full_path = os.path.dirname(os.path.abspath(__file__))
model = torch.hub.load(file_full_path+'\\ultralytics\\yolov5','yolov5s',source='local').to(device)

hwnd = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')
app = QApplication(sys.argv)
screen = QApplication.primaryScreen()

def func():
    shot = screen.grabWindow(hwnd).toImage()
    shot = QImageToCvMat(shot)

    xx = ScreenX // 2 - ShotW // 2
    yy = ScreenY // 2 - ShotH // 2
    shot = shot[xx:xx+ShotW, yy:yy+ShotH, :].copy()

    results = model(shot)
    choice = ((-1, -1), 100000000)
    data = results.pandas().xyxy[0].to_dict('index')
    # results.show()

    for i in range(0, len(data)):
        if data[i]['name'] != 'person':
            continue
        if data[i]['confidence'] < 0.5:
            continue 
        new_choice = calc_head(data[i])
        if choice[1] > new_choice[1]:
            choice = new_choice
    # print(choice)

    # shot = cv2.cvtColor(shot, cv2.COLOR_BGRA2RGB)
    # shot = cv2.circle(shot, choice[0], 3, (255, 255, 0), 3)
    # shot = cv2.circle(shot, (ScreenX // 2, ScreenY // 2), 3, (0, 0, 255), 3)
    # cv2.imshow('result', shot)
    # cv2.waitKey(1)
    return choice[0]


def aim(x):
    if x.name == 'x' and x.event_type == 'down':
        # print('biu~')
        choice = func()
        if choice == (-1, -1):
            pass
        else:
            xOffSet = choice[0] - CX
            yOffSet = choice[1] - CY
            pydirectinput.moveTo(CX + int(Tune * xOffSet), CY + int(Tune * yOffSet))
            time.sleep(0.2)
            aftermove = func()
# !!! 即只移动一倍，看看移动后还差多少

            print((choice[0] - 1280, choice[1] - 800), (aftermove[0] - 1280, aftermove[1] - 800)) 
            print('Tune should be: ', 1 / (1 - (aftermove[0] - 1280) / (choice[0] - 1280)))
# !!! Tune

        
keyboard.hook(aim)
keyboard.wait()


# while True:
#     choice = func()
#     if cv2.waitKey(1) == ord('c'):
#         break
    
cv2.destroyAllWindows()
# results.print()
# results.show()

# print(dir(shot))
# shot.save("screenshot.jpg")