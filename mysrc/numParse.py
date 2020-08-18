#!/usr/bin/env python3

import datetime,nfc

# PaSoRi RC-S380
PASORI_S380_PATH = 'usb:054c:06c3' # usb:vendorID abusolute identifier
studentNum = ""

def sc_from_raw(sc):
    return nfc.tag.tt3.ServiceCode(sc >> 6, sc & 0x3f)

def on_connect(tag):
    print("[{}] Connected".format(datetime.datetime.now().isoformat(' ','seconds')))
    sc1 = sc_from_raw(0x200B)
    bc1 = nfc.tag.tt3.BlockCode(0, service=0)
    bc2 = nfc.tag.tt3.BlockCode(1, service=0)
    block_data = tag.read_without_encryption([sc1], [bc1, bc2])
    global studentNum
    # int.from_bytes() requires Python 3.2 or later.
    #studentNum = int.from_bytes(block_data[1:9], byteorder='big') # It's not so important to convert bytearray to int...
    studentNum = block_data[1:9].decode("utf-8") # <class 'str'>
    print("Student ID: " + block_data[1:9].decode("utf-8"))
    #print("Shizudai ID: " + block_data[24:32].decode("utf-8"))
    return True

def main():
    print("[{}] Waiting for target. (Continue to press CTRL+C to halt.)".format(datetime.datetime.now().isoformat(' ', 'seconds')))
    with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
        clf.connect(rdwr={'on-connect': on_connect})
        return studentNum # returns 'str'

if __name__ == "__main__":
    main()
