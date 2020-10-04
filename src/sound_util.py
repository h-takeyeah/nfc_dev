import simpleaudio as sa
from datetime import datetime as dt

VOICE_LIST = {
    'ohayou': '../voice/ohayou.wav',
    'konnichiha': '../voice/konnichiha.wav',
    'konbanha': '../voicekonbanha.wav',
    'byebye': '../voice/byebye.wav',
    'otsukare': '../voice/otsukare.wav',
    'yarinaoshi': '../voice/yarinaoshi.wav',
    'internal_error': '../voice/internal_error.wav'
}

def play_voice(status):
    selif = ''
    h = dt.now().hour # 0 <= hour < 24
    if status == 'enter':
        if h >= 4 and h < 9:
            selif = 'ohayou'
        elif h >= 9 and h < 17:
            selif = 'konnichiha'
        else:
            selif = 'konbanha'

    elif status == 'exit':
        if h >= 9 and h < 17:
            selif = 'byebye'
        else:
            selif = 'otsukare'

    elif status == 'error':
        selif = 'yarinaoshi'

    else:
        selif = 'internal_error'
    
    try:
        wave_obj = sa.WaveObject.from_wave_file(VOICE_LIST[selif])
        play_obj = wave_obj.play()
        play_obj.wait_done()
        return True
    
    except FileNotFoundError as e:
        print('\033[01;31m## SOUND_UTIL ##')
        print('\033[01;31m{}'.format(e))
        print('## SOUND_UTIL ##\033[0m')
        """or did you encountered some sound trouble? HINT 'sudo raspi-config'"""
        return False

