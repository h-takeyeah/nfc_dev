#!/usr/bin/env python3

# NOTICE!!
# Run this code only for first time or after reset

import json
import mysql.connector
from auto_close_cursor import AutoCloseCursor as atclscur
from pathlib import Path

CONFIG_FILE = 'config.json'
MEMBERLIST_FILE = '../memberlist/memberlist_utf8.csv'

print(Path(MEMBERLIST_FILE).resolve())

TABLES = {}
TABLES['member_list'] = (
        "CREATE TABLE `member_list` ("
        "   `id` int(8) unsigned NOT NULL,"
        "   `name` varchar(60) NOT NULL,"
        "   `grade` year NOT NULL,"
        "   `is_holder` boolean NOT NULL DEFAULT 0,"
        "   PRIMARY KEY (`id`)"
        ")")

TABLES['in_room'] = (
        "CREATE TABLE `in_room` ("
        "   `id` int(8) unsigned NOT NULL,"
        "   `name` varchar(60) NOT NULL,"
        "   `mode` char(3) NOT NULL DEFAULT 'out',"
        "   PRIMARY KEY (`id`)"
        ")")

TABLES['room_entries'] = (
        "CREATE TABLE `room_entries` ("
        "   `id` int unsigned NOT NULL AUTO_INCREMENT,"
        "   `entered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "   `student_id` int(8) NOT NULL,"
        "   `student_name` varchar(60) NOT NULL,"
        "   INDEX(`id`)"
        ")")

TABLES['room_exits'] = (
        "CREATE TABLE `room_exits`("
        "   `id` int unsigned NOT NULL AUTO_INCREMENT,"
        "   `exited_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "   `student_id` int(8) NOT NULL,"
        "   `student_name` varchar(60) NOT NULL,"
        "   INDEX(`id`)"
        ")")

TABLES['error_log'] = (
        "CREATE TABLE `error_log`("
        "   `id` int unsigned NOT NULL AUTO_INCREMENT,"
        "   `happened_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "   `student_id` int(8) NOT NULL,"
        "   `student_name` varchar(60) NOT NULL,"
        "   INDEX(`id`)"
        ")")

with open(CONFIG_FILE) as f:
    cfg = json.load(f).get('sql_connector_parameters').get('maintenance')

try:
    cnx = mysql.connector.connect(**cfg)
    print('SQL connection established [{}]'.format(cnx.is_connected()))

    with atclscur(cnx) as cur:
        for table_name in TABLES:
            table_schema = TABLES[table_name]
            try:
                print('Creating table \'{}\'... '.format(table_name), end='')
                cur.execute(table_schema)
                
            except mysql.connector.ProgrammingError as e:
                print('\033[01;31mError\033[0m\n{}'.format(e))
            
            else: # Success
                print('OK')
        
        try:
            print('Inserting member info... ', end='')
            cur.execute('LOAD DATA LOCAL INFILE \'{}\' INTO TABLE {}.member_list FIELDS TERMINATED BY \',\' IGNORE 1 LINES'.format(Path(MEMBERLIST_FILE).resolve(), cfg.get('database')))
            cnx.commit() # Do not forget 'connector.commit()'.
        
        except mysql.connector.Error as e:
            print('\033[01;31mError\033[0m\n{}'.format(e))

        else: # Success
            print('OK')

except:
    import traceback
    traceback.print_exc()

