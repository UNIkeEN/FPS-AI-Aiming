import pyaudio              

class audio:
    def __init__(self):
        pass

    def findDevice(name,mode):
        if mode=="input" or mode=="i":
            check = 'maxInputChannels'       
        elif mode=="output" or mode=="o":
            check = 'maxOutputChannels'
        else:
            print ("Wrong mode! Please give a string like 'input' or 'i', 'output' or 'o'")
            return None   

        p = pyaudio.PyAudio()       
        num = p.get_device_count()     

        for i in range(0, num):          
            device = p.get_device_info_by_index(i)
            if device.get(check) >0 and name in device.get('name'):
                p.terminate()
                return i
        p.terminate()

    
