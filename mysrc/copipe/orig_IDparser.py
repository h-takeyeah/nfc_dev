#!/usr/bin/env python3

import sys
import nfc

# PaSoRi RC-S380
#PASORI_S380_PATH = 'usb:001:004' # usb:bus:device rerative
PASORI_S380_PATH = 'usb:054c:06c3' # usb:vendorID abusolute identifier

def sc_from_raw(sc):
    return nfc.tag.tt3.ServiceCode(sc >> 6, sc & 0x3f)

def on_startup(targets):
    return targets

def on_connect(tag):
    print("[*] connected:", tag)
    sc1 = sc_from_raw(0x200B)
    bc1 = nfc.tag.tt3.BlockCode(0, service=0)
    bc2 = nfc.tag.tt3.BlockCode(1, service=0)
    block_data = tag.read_without_encryption([sc1], [bc1, bc2])
    print("Student ID: " + block_data[1:9].decode("utf-8"))
    print("Shizudai ID: " + block_data[24:32].decode("utf-8"))
    return True

def on_release(tag):
    print("[*] released: ", tag)

def main(args):
    with nfc.ContactlessFrontend(PASORI_S380_PATH) as clf:
        while clf.connect(rdwr={
            'on-startup': on_startup,
            'on-connect': on_connect,
            'on-release': on_release,
            }):
                pass

if __name__ == "__main__":
    main(sys.argv)
