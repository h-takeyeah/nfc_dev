import random
import simpleaudio as sa
from datetime import datetime as dt

VOICE_LIST = {
    'kanryou': '../voice/kanryou.wav',
    'konbanha': '../voice/konbanha.wav',
    'konnichiha': '../voice/konnichiha.wav',
    'matakitene': '../voice/matakitene.wav',
    'mattetayo': '../voice/mattetayo.wav',
    'ohayou': '../voice/ohayou.wav',
    'otsukare': '../voice/otsukare.wav',
    'oyasumi': '../voice/oyasumi.wav',
    'pita': '../voice/pita.wav',
    'seikou': '../voice/seikou.wav',
    'shippai': '../voice/shippai.wav',
    'tappushitene': '../voice/tappushitene.wav'
}

SOUND_LIST = {}

def play_voice(action):
    selif = ''
    h = dt.now().hour # 0 <= hour < 24
    if action == 'enter':
        if h >= 4 and h < 9:
            selif = 'ohayou'
        elif h >= 9 and h < 16:
            selif = 'konnichiha'
        else:
            selif = 'konbanha'
        
        # omake
        if random.randrange(100) % 3 == 0:
            selif = 'mattetayo'

    elif action == 'exit':
        if h >= 4 and h < 16:
            selif = 'matakitene'
        elif h >= 16 and h < 20:
            selif = 'otsukare'
        else:
            selif = 'oyasumi'

    elif action == 'error':
        selif = 'shippai'

    else:
        selif = 'shippai'
    
    try:
        wave_obj = sa.WaveObject.from_wave_file(VOICE_LIST[selif])
        play_obj = wave_obj.play()
        #play_obj.wait_done()
        return True
    
    except FileNotFoundError as e:
        print('\033[;33m## == Info from SOUND_UTIL ==')
        print('##  \033[01;31m{}\033[0m\n'.format(e))
        """or did you encountered some sound trouble? HINT 'sudo raspi-config'"""
        return False

def beep(event):
    pass

