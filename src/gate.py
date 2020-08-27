#!/usr/bin/env python3

import csv,nfc,sys
from pathlib import Path
from datetime import datetime

LOG_FILE = '../log/' + str(datetime.now().date())
MEMBERLIST_FILE = '../memberlist/memberlist_utf8.csv'

# PaSoRi RC-S380
PASORI_S380_PATH = 'usb:054c:06c3' # usb:{vendorID}:{productID}

def writeLog(student_num, student_name):
    if not Path(LOG_FILE).parent.exists(): # If log dir does not exists, create it
        Path(LOG_FILE).parent.mkdir()

    try:
        logpath = Path('{}.csv'.format(LOG_FILE))
        status = '-' # Unknown student

        if logpath.is_file(): # Check if logfile exists
            if not student_name == 'Unknown':
                with logpath.open(mode='r') as logfile:
                    current_log = csv.reader(logfile)
                    counter = 0
                    for row in current_log:
                        if row[2] == student_num:
                            counter += 1

                    if counter % 2 == 0:
                        status = 'enter'
                    else:
                        status = 'leave'

            with logpath.open(mode='a',newline='') as outfile: # mode='a': append
                writer = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                dt = datetime.now()
                writer.writerow([dt.date(), dt.time().isoformat('seconds'), student_num, student_name, status])

        else:
            if not student_name == 'Unknown':
                status = 'enter'

            with logpath.open(mode='w',newline='') as outfile: # mode='w': write (create & write)
                writer = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                dt = datetime.now()
                writer.writerow([dt.date(), dt.time().isoformat('seconds'), student_num, student_name, status])
                print('\033[01;34m[{}] Created a log file: {}.csv\033[0m'.format(datetime.now().isoformat(' ', 'seconds'), LOG_FILE)) # Text color blue

        if status == 'enter':
            print('\033[01;35m[{}] Recorded. Welcome!(^_^)/~ {}\033[0m'.format(datetime.now().isoformat(' ', 'seconds'), student_name)) # Text color magenta
            
        elif status == 'leave':
            print('\033[01;36m[{}] Recorded. Bye!(^_^)/~ {}\033[0m'.format(datetime.now().isoformat(' ', 'seconds'), student_name)) # Text color syan

        elif status == '-':
            print('\033[01;41m[{}] Recorded.\033[0m'.format(datetime.now().isoformat(' ', 'seconds'))) # Text bg color red

    except (NotADirectoryError, IsADirectoryError) as e:
        print('\033[01;31m{}\033[0m'.format(e)) # Text color red
        sys.exit(0)

def lookup(q):
    print('[{}] Looking for {}...'.format(datetime.now().isoformat(' ','seconds'), q))
    try:
        memberPath = Path(MEMBERLIST_FILE)
        with memberPath.open(mode='r', newline='', encoding='utf8') as dic:
            memberlist = csv.reader(dic)
            foundFlag = False
            next(memberlist) # Skip header
            for row in memberlist:
                if row[0] == q:
                    foundFlag = True
                    print('\033[01;32m[{}] Found \'Number:{}, Name:{}\'\033[0m'.format(datetime.now().isoformat(' ', 'seconds'), row[0], row[1])) # Text color green
                    writeLog(row[0], row[1]) # member
                    break
                else:
                    pass # Do nothing

            if not foundFlag:
                print('\033[01;41m[{}] Unknown student \'Number:{}, Name:Unknown\'\033[0m'.format(datetime.now().isoformat(' ', 'seconds'), q)) # Text bg color red
                writeLog(q, 'Unknown') # Unknown student

    except FileNotFoundError as e:
        print('\033[01;31m{}\033[0m'.format(e)) # Text color red
        sys.exit(0)

# NFC methods
# https://qiita.com/pf_packet/items/9a50d9f3b1f478930b02
def sc_from_raw(sc):
    return nfc.tag.tt3.ServiceCode(sc >> 6, sc & 0x3f)

def on_startup(targets):
    return targets

def on_connect(tag):
    print('\n[{}] Connected'.format(datetime.now().isoformat(' ', 'seconds')))
    try:
        sc1 = sc_from_raw(0x200B)
        bc1 = nfc.tag.tt3.BlockCode(0, service=0) # To get student number
        #bc2 = nfc.tag.tt3.BlockCode(1, service=0) # To get shizdai ID
        block_data = tag.read_without_encryption([sc1], [bc1]) #block_data = tag.read_without_encryption([sc1], [bc1,bc2])
        lookup(block_data[1:9].decode('utf-8')) # Start searching
    
    except nfc.tag.TagCommandError as e: # Too short touch raises this error
        print('\033[01;31m{}\n\033[01;33mPlease touch your card again\033[0m'.format(e)) # Text color red

    return True # TODO This method always returns True. Is it good?

def on_release(tag):
    print('[{}] Released'.format(datetime.now().isoformat(' ', 'seconds')))

def main():
    print('[{}] Session begin. Press CTRL+C to stop'.format(datetime.now().isoformat(' ', 'seconds')))
    with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
        while clf.connect(rdwr={
            'on-startup': on_startup,
            'on-connect': on_connect,
            'on-release': on_release,
            }):
            pass

if __name__ == "__main__":
    main()

