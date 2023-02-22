from win32 import win32api, win32gui, win32print
from win32.lib import win32con

hDC = win32gui.GetDC(0)
w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)  # 横向分辨率
h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)  # 纵向分辨率
print(w)
print(h)