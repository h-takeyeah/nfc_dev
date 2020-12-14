#!/bin/bash
HOSTNAME="localhost"
PORT="3306"
DATA_TO_INSERT="./memberlist/memberlist_utf8.csv"

echo "Enter password for root(not unix root)"
echo -n "Enter password: "
read ROOTPASS
echo -e "\nEnter password for normal(new)"
echo -n "Enter password: "
read NORMALPASS
echo "password for 'normal': ${NORMALPASS}" >> ./log/setup_db_`date "+%F"`.log
echo "OK"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "CREATE DATABASE IF NOT EXISTS accessdb"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "CREATE USER IF NOT EXISTS normal@'localhost' IDENTIFIED BY '${NORMALPASS}'"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "GRANT ALL ON accessdb.* TO normal@'localhost'"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose < ./schema/create_table_access_log.sql
echo "END"
