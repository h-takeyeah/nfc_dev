#!/usr/bin/env python3

import datetime,csv,nfc

LOG_FILE = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month)

# PaSoRi RC-S380
PASORI_S380_PATH = 'usb:054c:06c3' # usb:{vendorID}:{productID}

def writeLog(student_id, student_name):
    with open('../log/{}.csv'.format(LOG_FILE), 'a') as outfile: # mode='a': append
        writer = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # memo
        # quotechar='"': abc -> "abc"
        # quoting=csv.QUOTE_ALL: a,b,c -> "a","b","c"
        dt = datetime.datetime.now()
        writer.writerow([student_id, student_name, dt.date(), dt.time().isoformat('seconds')])
        print("[{}] Recorded".format(datetime.datetime.now().isoformat(' ', 'seconds')))

def lookup(q):
    print('[{}] Looking for {}...'.format(datetime.datetime.now().isoformat(' ','seconds'), q))
    with open(file='../memberlist/memberlist_utf8.csv', mode='r', newline='',encoding='utf8') as input:
        memberlist = csv.reader(input)
        foundFlag = False
        next(memberlist) # Skip header
        for row in memberlist:
            if row[0] == q:
                foundFlag = True
                print('\033[01;32m[{}] Found \'ID:{}, Name:{}\'\033[0m'.format(datetime.datetime.now().isoformat(' ', 'seconds'), row[0], row[1])) # Text color green
                writeLog(row[0], row[1]) # member
                break
            else:
                pass # Do nothing
            pass

        if foundFlag == False:
            writeLog(q, 'Unknown') # Not a member
            print('\033[01;31m[{}] ITS has no member whose ID is \'{}\'\033[0m'.format(datetime.datetime.now().isoformat(' ', 'seconds'), q)) # Text color red
            pass
        pass
    pass

def sc_from_raw(sc):
    return nfc.tag.tt3.ServiceCode(sc >> 6, sc & 0x3f)

def on_startup(targets):
    return targets

def on_connect(tag):
    print('\n[{}] Connected'.format(datetime.datetime.now().isoformat(' ', 'seconds')))
    sc1 = sc_from_raw(0x200B)
    bc1 = nfc.tag.tt3.BlockCode(0, service=0)
    bc2 = nfc.tag.tt3.BlockCode(1, service=0)
    block_data = tag.read_without_encryption([sc1], [bc1, bc2])
    lookup(block_data[1:9].decode('utf-8')) # Start searching
    return True

def on_release(tag):
    print('[{}] Released'.format(datetime.datetime.now().isoformat(' ', 'seconds')))
    pass


def main():
    print('[{}] Session begin. Press CTRL+C to halt'.format(datetime.datetime.now().isoformat(' ', 'seconds')))
    with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
        while clf.connect(rdwr={
            'on-startup': on_startup,
            'on-connect': on_connect,
            'on-release': on_release,
            }):
            pass

if __name__ == "__main__":
    main()
