import os,json
import time

file_full_path = os.path.dirname(os.path.abspath(__file__))

try:
    from audio import audio
    import pyaudio
    import viVoicecloud as vv
    
except:
    print("相关音频依赖库未安装,音频服务启动失败")
    time.sleep(1)
    os._exit(0)

device_in = audio.findDevice("ac108","input")
Sample_channels = 1  
Sample_rate = 16000  
Sample_width = 2         
time_seconds = 0.5

p = pyaudio.PyAudio()
stream = p.open(
            rate=Sample_rate,
            format=p.get_format_from_width(Sample_width),
            channels=Sample_channels,
            input=True,
            input_device_index=device_in,
            start=False)

vv.Login()
ASR=vv.asr()
while True:
    try:
        ASR.SessionBegin(language='Chinese')
        stream.start_stream()
        status=0
        while status!=3:
            frames=stream.read(int(Sample_rate*time_seconds),exception_on_overflow = False)
            ret,status,recStatus=ASR.AudioWrite(frames)
        
        stream.stop_stream()
        words=ASR.GetResult()
        ASR.SessionEnd()
        # print (words)
        if words=='瞄准关闭':
            file_full_path = os.path.dirname(os.path.abspath(__file__))
            filename=file_full_path+'\\running_status.json'
            run_status=0
            with open(filename,'w') as file_obj:
                json.dump(run_status,file_obj)
            os._exit(0)

    except Exception as e:
        print(e)
        print('stopped')
        vv.Logout()
        stream.close()
        p.terminate()
        break

