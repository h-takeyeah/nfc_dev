import simpleaudio as sa
from datetime import datetime as dt
class SoundUtil:
    VOICE_LIST = ['konnichiha': '../voice/konnichiha.wav', 'otsukare3': '../voice/otsukare3.wav']
    def play_voice(self, status):
        selif = ''
        h = dt.now().hour
        if status = 'enter':
            if h >= 4 and h < 9:
                selif = 'ohayou'
            elif h >= 9 and h < 17:
                selif = 'konnichiha'
            else:
                selif = 'konbanha'

        elif status = 'exit':
            if h >= 9 and h < 17:
                selif = 'otsukare3'
            else:
                selif = 'otukare'

            if selif in self.VOICE_LIST:
                wave_obj = sa.WaveObject.from_wave_file(self.VOICE_LIST[s])
                play_obj = wave_obj.play()
                play_obj.wait_done()
                return
            else:
                print('(SOUND_UTIL) audio file(.wav) not found.')
        else: # do nothing
            return
