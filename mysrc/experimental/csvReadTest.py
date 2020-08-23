#!/usr/bin/env python3

import csv

def main():
    with open('../memberlist/memberlist_utf8.csv', newline='') as csvfile:
        members = csv.reader(csvfile, delimiter=',') # create a reader object
        #print(next(members)) # iterator's __next()__
        with open('../')
        for row in members:
            print(row[0])

if __name__ == '__main__':
    main()
