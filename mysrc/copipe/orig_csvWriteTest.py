#!/usr/bin/env python3

import csv

def main():
    with open('./history08.csv', 'w') as outfile: # mode='w': open for writing
        writer = csv.writer(outfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL) 
        # quotechar='"': abc -> "abc"
        # quoting=csv.QUOTE_MINIMAL: a,b,c -> 
        writer.writerow(['Spam'] * 5 + ['Baked Beans'])
        writer.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])

if __name__ == '__main__':
    main()
