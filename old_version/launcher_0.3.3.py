import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
import json
import os
import time
from ttkbootstrap.dialogs import Messagebox

winSizeX,winSizeY = 680,460

root = ttk.Window(
    title="FPS AI Aiming - Launcher",
    themename="superhero",
    size=(winSizeX,winSizeY),
    resizable=(False,False),
    )
root.place_window_center()

id_game=ttk.IntVar()
id_model=ttk.IntVar()
id_runtype=ttk.IntVar()
id_game.set(2)
id_model.set(1)
id_runtype.set(2)
run_status=ttk.IntVar()
run_status.set(0)

GAMES = [
    ("CS 1.6", 1),
    ("CS : GO", 2),
    ("Apex Legends", 3)]

MODELS = [
    (" yolov5n ", 1),
    (" yolov5s ", 2),
    (" yolov5m ", 3)]

RUNTYPE = [
    ("   Demo   ", 1),
    ("  Normal  ", 2),
    ("   Beta   ", 3)]

label_title = ttk.Label(root,
    text=" FPS AI AIMING",
    font=('Helvetica',30),
    bootstyle="light")
label_title.pack(side=TOP, pady=(20,0))

label_version = ttk.Label(root,text="       v0.3.3\n20220714",bootstyle="secondary")
label_version.place(x=winSizeX-100, y=winSizeY-60, anchor=NW)

container1 = ttk.Frame(root)
container1.place(x=30,y=120, anchor=NW)

label_sign1 = ttk.Label(container1,
    text="Choose the game    ",
    font=('Helvetica',12),
    bootstyle="secondary")
label_sign1.pack(side=LEFT, pady=20, padx=20)

for games, num in GAMES:
    rbutton_game = ttk.Radiobutton(container1, text=games, variable=id_game, value=num, bootstyle="info-toolbutton")
    rbutton_game.pack(side=LEFT, padx=3)

container2 = ttk.Frame(root)
container2.place(x=30,y=180, anchor=NW)

def showModelWarn():
    num = id_model.get()
    WARN = {
        1 : " - Recommand at All Services",
        2 : " - Recommand at RTX3050 and above",
        3 : " - Recommand at RTX3080 and above"
    }
    label_warn.configure(text=WARN.get(num))

label_sign2 = ttk.Label(container2,
    text="Choose the model   ",
    font=('Helvetica',12),
    bootstyle="secondary")
label_sign2.pack(side=LEFT, pady=20, padx=20)

label_warn = ttk.Label(root,
    text=" - Recommand at All Services",
    font=('Helvetica',8),
    bootstyle="light")
label_warn.place(x=290,y=245, anchor=NW)

for models, num in MODELS:
    rbutton_model = ttk.Radiobutton(container2, text=models, variable=id_model, value=num, bootstyle="info-toolbutton", 
        command=showModelWarn)
    rbutton_model.pack(side=LEFT, padx=3)

container3 = ttk.Frame(root)
container3.place(x=30,y=265, anchor=NW)

def showModelWarn2():
    num = id_runtype.get()
    WARN = {
        1 : " - Show the AI detect process window",
        2 : " - Run in normal mode",
        3 : " - Try the beta function : dynamic prediction"
    }
    label_warn2.configure(text=WARN.get(num))

label_sign2 = ttk.Label(container3,
    text="Choose the run-type",
    font=('Helvetica',12),
    bootstyle="secondary")
label_sign2.pack(side=LEFT, pady=20, padx=20)

for ltype, num in RUNTYPE:
    rbutton_runtype = ttk.Radiobutton(container3, text=ltype, variable=id_runtype, value=num, bootstyle="info-toolbutton",
        command=showModelWarn2)
    rbutton_runtype.pack(side=LEFT, padx=3)

label_warn2 = ttk.Label(root,
    text=" - Run in normal mode",
    font=('Helvetica',8),
    bootstyle="light")
label_warn2.place(x=290,y=330, anchor=NW)

def Run():
    file_full_path = os.path.dirname(os.path.abspath(__file__))
    if run_status.get()==0:
        params={'game':id_game.get(), 'model': id_model.get(),'runtype': id_runtype.get()}
        filename=file_full_path+'\\bin\\launcher_params.json'
        with open(filename,'w') as file_obj:
            json.dump(params,file_obj)
        os.system('start pythonw '+file_full_path+'\\bin\\ai_0.3.1.py')
        if id_runtype.get() == 1:
            os.system('start pythonw '+file_full_path+'\\bin\\demo.py')
        run_status.set(1)
        filename=file_full_path+'\\bin\\running_status.json'
        with open(filename,'w') as file_obj:
            json.dump(run_status.get(),file_obj)
        btnRun.configure(text="  End the AI Aiming~  ", bootstyle="danger")
        root.title("FPS AI Aiming - Launcher [Running] ")
        print("show_info: ",Messagebox.show_info(
            message=" AI-Aiming已启动\n 首次使用或切换模型需下载模型文件,请稍等\n > 按【X】键自动瞄准并射击\n > 点击启动器的End按钮或关闭启动器以结束AI-Aiming   ",title="Tips",alert=False))  
    else:
        filename=file_full_path+'\\bin\\running_status.json'
        run_status.set(0)
        with open(filename,'w') as file_obj:
            json.dump(run_status.get(),file_obj)
        btnRun.configure(text="  Run the AI Aiming!  ", bootstyle="secondary")
        root.title("FPS AI Aiming - Launcher")
    
    
btnRun = ttk.Button(root,
    text="  Run the AI Aiming!  ",
    bootstyle="secondary",
    command=Run)
btnRun.pack(side=BOTTOM, pady=35)

def close_window():
    file_full_path = os.path.dirname(os.path.abspath(__file__))
    filename=file_full_path+'\\bin\\running_status.json'
    run_status.set(0)
    with open(filename,'w') as file_obj:
        json.dump(run_status.get(),file_obj)
    os._exit(0)

root.protocol('WM_DELETE_WINDOW',close_window)
root.mainloop()
