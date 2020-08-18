#!/usr/bin/env python3

import datetime,csv,numParse

HIST_FILE = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) # TODO {YY-MM} Is this best?

def main():
    with open('../history/{}.csv'.format(HIST_FILE), 'a') as outfile: # mode='a': append
        while True:
            writer = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL) 
            # memo
            # quotechar='"': abc -> "abc"
            # quoting=csv.QUOTE_ALL: a,b,c -> "a","b","c"
            dt = datetime.datetime.now()
            num = numParse.main()
            writer.writerow([num, dt.date(), dt.time().isoformat('seconds')])
            print("[{}] Completed".format(datetime.datetime.now().isoformat(' ', 'seconds')))

if __name__ == '__main__':
    main()
