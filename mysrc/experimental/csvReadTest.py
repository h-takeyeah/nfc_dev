#!/usr/bin/env python3

import csv

def main():
    with open('./non_holder_list.csv') as csvfile:
        holder = csv.reader(csvfile, delimiter=',') # create a reader object
        for row in holder:
            print(row)

if __name__ == '__main__':
    main()
