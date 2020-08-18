#!/usr/bin/env python3

import nfc

clf = nfc.ContactlessFrontend()
assert clf.open('usb:001:004') is True
assert clf.open('usb:054c:06c3') is True
assert clf.open('usb:001') is True
assert clf.open('usb:054c') is True
assert clf.open('usb') is True
print(clf)
clf.close()
 
