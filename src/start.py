#! /usr/bin/env python3

import nfc
import sys
import soundutils as su
import connectionutils as con

PASORI_S380_PATH = 'usb:054c:06c3'


def run():
    """メインルーチン
    これがずっと回る

    """
    try:
        with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
            while clf.connect(rdwr={'on-connect': on_connect}):
                pass

    except OSError as ose:
        print('\033[01;31m[!]\033[0m {}'.format(ose))
        su.play_voice('error')
        print('\033[01;31m[!]\033[0m Stop')
        exit(-1)


def on_connect(tag):
    """This function is called when a remote tag has been activated.
        カードにアクセスできた後の処理はこの関数を起点にして行う

    Parameters
    ----------
        tag : nfc.tag.Tag

    Returns
    -------

    """
    print('\033[01;32m[*]\033[0m Card touched.')
    try:
        sc = nfc.tag.tt3.ServiceCode(0x200B >> 6, 0x200B & 0x3f)
        bc = nfc.tag.tt3.BlockCode(0, service=0)  # To get student ID
        block_data = tag.read_without_encryption([sc], [bc])

    except nfc.tag.TagCommandError as e:
        su.play_voice('warning')

        """
        cf. https://github.com/nfcpy/nfcpy/blob/master/src/nfc/tag/__init__.py
        0x01A6 => "invalid service code number or attribute"
        0x0(nfc.tag.TIMEOUT_ERROR) => "unrecoverable timeout error"
        """
        if e.errno == 0x1A6:
            print('\033[01;33m[!]\033[0m \
Your IC card seems to be unavailable. Is it valid one?\n')
        elif e.errno == 0x0:
            print('\033[01;33m[!]\033[0m \
Too short. Please touch your card again\n')
        else:
            print('\033[01;33m[!]\033[0m {}\n'.format(e))

        return False

    student_id = int(block_data[1:9].decode('utf-8'))

    if con.is_inroom(student_id):
        if con.leave_room(student_id):
            su.play_voice('exit')
        else:
            su.play_voice('error')
            return False

    else:
        if con.enter_room(student_id):
            su.play_voice('enter')
        else:
            su.play_voice('error')
            return False

    return True


if __name__ == "__main__":
    print('\033[01;32m[*]\033[0m Hello!')
    print('\033[01;32m[*]\033[0m Waking up... ', end='')
    if not con.ping_test():
        print('Failed', file=sys.stderr)
        su.play_voice('error')
        print('\033[01;31m[!]\033[0m Stop', file=sys.stderr)
        exit(-1)
    else:
        print('Success')

    print('\033[01;32m[*]\033[0m Now main routine started \
-- Press Ctrl+C to stop.\n')
    run()
