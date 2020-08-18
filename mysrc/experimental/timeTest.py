#!/usr/bin/env python3

import datetime
today = datetime.datetime.now().date()
now = datetime.datetime.now().time()
print(today)
print(type(today))
print(now.isoformat('seconds'))
print(type(now))
