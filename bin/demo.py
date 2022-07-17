from pickle import FALSE
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
from cv2 import cvtColor
import win32gui
import sys
import pydirectinput
import cv2
import numpy as np
import keyboard
import torch
import time
import os
import win32con

cvWindowsName='Detect CS:GO'
ScreenX = 2560
ScreenY = 1660
from screeninfo import get_monitors
for m in get_monitors():
    if m.is_primary:
        ScreenX = m.width
        ScreenY = m.height
CX = ScreenX // 2
CY = ScreenY // 2


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


# 初始化部分
pydirectinput.PAUSE = 0
# pydirectinput.FAILSAFE = False
device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
file_full_path = os.path.dirname(os.path.abspath(__file__))
model = torch.hub.load(file_full_path+'\\ultralytics\\yolov5','yolov5n',source='local').to(device)

hwnd = win32gui.FindWindow(None, 'Counter-Strike: Global Offensive - Direct3D 9')
app = QApplication(sys.argv)
screen = QApplication.primaryScreen()

def func():
    # 持续循环、检测、圈头
    shot1 = screen.grabWindow(hwnd).toImage()
    shot1 = QImageToCvMat(shot1)
    results1 = model(shot1)
    img = cvtColor(shot1, cv2.COLOR_BGRA2RGB)
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
        if new_choice[0] != (-1, -1):    
            img = cv2.rectangle(img, (int(data1[i]['xmin']), int(data1[i]['ymin'])), (int(data1[i]['xmax']), int(data1[i]['ymax'])), (255, 100, 100), 4)
            img = cv2.circle(img, new_choice[0], 10, (0, 0, 200), 5)

    cv2.namedWindow(cvWindowsName,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(cvWindowsName,ScreenX//4,ScreenY//4)
    # shot = cv2.circle(shot, (ScreenX // 2, ScreenY // 2), 3, (0, 0, 255), 3)
    cv2.imshow(cvWindowsName, img)
    hwnd2=win32gui.FindWindow(None, cvWindowsName)
    CVRECT=cv2.getWindowImageRect(cvWindowsName)
    win32gui.SetWindowPos(hwnd2, win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    cv2.waitKey(1)

filename2 = file_full_path+'\\running_status.json'
while True:
    with open(filename2, 'r') as ss:
        func()
        if ss.read() == '0':
            break
        
cv2.destroyAllWindows()