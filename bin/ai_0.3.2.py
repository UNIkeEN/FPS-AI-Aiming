from pickle import FALSE
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from pytest import param
import win32gui
import sys
import pydirectinput
import cv2
import numpy as np
import keyboard
import torch
import time
import json
import os

file_full_path = os.path.dirname(os.path.abspath(__file__))
filename=file_full_path+'\\launcher_params.json'

with open(filename, "r") as f:
    params = json.load(f)


ScreenX = 2560
ScreenY = 1660
from screeninfo import get_monitors
for m in get_monitors():
    if m.is_primary:
        ScreenX = m.width
        ScreenY = m.height
CX = ScreenX // 2
CY = ScreenY // 2

Tune = 2.4 / params['mouse_sen'] # 适配csgo的加速值
if params['runtype'] == 2:
    LOOK_TWICE = False # 要不要看两次然后打运动靶
else:
    LOOK_TWICE = True

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
    head_x = int((p['xmin'] + p['xmax']) // 2)
    head_y = int(p['ymin'] + (p['xmax'] - p['xmin']) / 4)
    dis = abs(head_x - ScreenX // 2) + abs(head_y - ScreenY // 2)

    if p['xmin'] > ScreenX * 1200 / 2560 and p['xmax'] > ScreenX * 1550 / 2560 and p['ymin'] < 1400 * ScreenY / 1600 and p['ymax'] > 1550 * ScreenY / 1600 :
        # 排除掉自己手
        head_x = -1
        head_y = -1
        dis = 1e5

    return ((head_x, head_y), dis)


if params['model'] == 1:
    modelname = 'yolov5n'
if params['model'] == 2:
    modelname = 'yolov5s'
if params['model'] == 3:
    modelname = 'yolov5m'
# 初始化部分
pydirectinput.PAUSE = 0
# pydirectinput.FAILSAFE = False
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
file_full_path = os.path.dirname(os.path.abspath(__file__))
model = torch.hub.load(file_full_path+'\\ultralytics\\yolov5',modelname,source='local').to(device)

hwnd = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')
app = QApplication(sys.argv)
screen = QApplication.primaryScreen()

def func():
    # 每次按下x键调用的函数
    # 包括两次的 截图、图片喂ai，选择目标
    # 和一次的运动计算补偿
    shot1 = screen.grabWindow(hwnd).toImage()
    shot1 = QImageToCvMat(shot1)
    results1 = model(shot1)

    choice1 = ((-1, -1), 1e5)
    data1 = results1.pandas().xyxy[0].to_dict('index')
    for i in range(0, len(data1)):
        if data1[i]['name'] != 'person':
            continue
        if data1[i]['confidence'] < 0.3:
            continue 
        new_choice = calc_head(data1[i])
        if choice1[1] > new_choice[1]:
            choice1 = new_choice
    # 第一轮结束
    if LOOK_TWICE:
        shot2 = screen.grabWindow(hwnd).toImage()
        shot2 = QImageToCvMat(shot2)
        results2 = model(shot2)
        choice2 = ((-1, -1), 1e5)
        data2 = results2.pandas().xyxy[0].to_dict('index')
        for i in range(0, len(data2)):
            if data2[i]['name'] != 'person':
                continue
            if data2[i]['confidence'] < 0.5:
                continue 
            new_choice = calc_head(data2[i])
            if choice2[1] > new_choice[1]:
                choice2 = new_choice

        """
        从发出截图指令到处理完成约 0.08s
        单单截图约耗时 0.02s
        移动鼠标耗时 0.006以内
        """
        xmove = choice2[0][0] - choice1[0][0]
        ymove = choice2[0][1] - choice1[0][1]

        # 忽略移动鼠标的时间，在两次截图中目标视为匀速移动，补上相同的位移差值
        return (choice2[0][0] + xmove, choice2[0][1] + ymove)
    else:
        return choice1[0]


def aim(x):
    if (x.name == 'x' or x.name == 'X') and x.event_type == 'down':
        print('biu~')
        choice = func()
        if choice == (-1, -1):
            pass
        else:
            xOffSet = choice[0] - CX
            yOffSet = choice[1] - CY
            print('choice', choice)
            print('moveto', (CX + int(Tune * xOffSet), CY + int(Tune * yOffSet)))
            pydirectinput.moveTo(CX + int(Tune * xOffSet), CY + int(Tune * yOffSet))
            pydirectinput.click()

filename2 = file_full_path+'\\running_status.json'
keyboard.hook(aim)
while True:
    with open(filename2, 'r') as ss:
        if ss.read() == '0':
            break
# keyboard.wait()
cv2.destroyAllWindows()