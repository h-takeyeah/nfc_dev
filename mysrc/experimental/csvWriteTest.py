#!/usr/bin/env python3

import datetime,csv,numParse

HIST_FILE = str(datetime.datetime.now().year) + '-' + str(datetime.datetime.now().month) # TODO {YY-MM} Is this best?

def main():
    with open('../../memberlist/memberlist_utf8.csv', newline='') as source:
        members = csv.reader(source, delimiter=',') # create a reader object
        with open('../../history/{}.csv'.format(HIST_FILE), 'a') as outfile: # mode='a': append
            while True:
                writer = csv.writer(outfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL) 
                # memo
                # quotechar='"': abc -> "abc"
                # quoting=csv.QUOTE_ALL: a,b,c -> "a","b","c"
                dt = datetime.datetime.now()
                num = numParse.main()
                #for row in members:
                #    print(type(row))
                #    print(type(row[0]))
                #    print(type(row[1]))
                #    break
                #    if (num == row[0]):
                writer.writerow([num, dt.date(), dt.time().isoformat('seconds')])
                print("[{}] Completed".format(datetime.datetime.now().isoformat(' ', 'seconds')))
                #        break

if __name__ == '__main__':
    main()
