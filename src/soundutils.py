import random
import simpleaudio as sa
from datetime import datetime as dt

AUDIO_LIST = {
    'kanryou': '../audio/kanryou.wav',
    'konbanha': '../audio/konbanha.wav',
    'konnichiha': '../audio/konnichiha.wav',
    'matakitene': '../audio/matakitene.wav',
    'mattetayo': '../audio/mattetayo.wav',
    'ohayou': '../audio/ohayou.wav',
    'otsukare': '../audio/otsukare.wav',
    'oyasumi': '../audio/oyasumi.wav',
    'pita': '../audio/pita.wav',
    'seikou': '../audio/seikou.wav',
    'shippai': '../audio/shippai.wav',
    'tappushitene': '../audio/tappushitene.wav',
    'shippai': '../audio/shippai.wav',
    'enter': '../audio/correct_answer3.wav',
    'exit': '../audio/decision4.wav',
    'warning': '../audio/warning1.wav'
}


def play_voice(action):
    """音声ファイル(.wav)を再生する。セリフ用

    Args:
        action: str

    Returns:
       bool

    """
    selif = None
    h = dt.now().hour  # 0 <= hour < 24
    if action == 'enter':
        selif = ['enter']
        if h >= 4 and h < 9:
            selif.append('ohayou')
        elif h >= 9 and h < 16:
            selif.append('konnichiha')
        else:
            selif.append('konbanha')

        # omake
        if random.randrange(100) % 3 == 0:
            selif.append('mattetayo')

    elif action == 'exit':
        selif = ['exit']
        if h >= 4 and h < 16:
            selif.append('matakitene')
        elif h >= 16 and h < 20:
            selif.append('otsukare')
        else:
            selif.append('oyasumi')

    elif action == 'warning':
        selif = ['warning']

    else:
        selif = ['warning', 'shippai']

    emit(selif)
    return


def emit(words):
    """セリフを発話させる

    Parameters
    ----------
        words : list

    Returns
    -------
        成功したらTrue、ファイルが見つからなくて失敗したらFalse

    """
    for key in words:
        try:
            wave_obj = sa.WaveObject.from_wave_file(AUDIO_LIST[key])
            play_obj = wave_obj.play()
            play_obj.wait_done()

        except FileNotFoundError as e:
            print('\033[;33m[!]\033[0m {}\n'.format(e))
            """Or did you encounter some sound trouble?
            HINT 'sudo raspi-config'
            """
            return False

    return True
