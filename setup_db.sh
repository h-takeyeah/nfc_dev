#!/bin/bash
HOSTNAME="localhost"
PORT="3306"
DATA_TO_INSERT="./memberlist/memberlist_utf8.csv"

echo "Enter password for root(not unix root)"
echo -n "Enter password: "
read ROOTPASS
echo -e "\nEnter password for nomal user(new)"
echo -n "Enter password: "
read NOMALPASS
echo "password for 'nomal' user: ${NOMALPASS}" >> ./log/setup_db_`date "+%F"`.log
echo "OK"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "CREATE DATABASE IF NOT EXISTS accessdb"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "CREATE USER IF NOT EXISTS nomal@'localhost' IDENTIFIED BY '${NOMALPASS}'"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "GRANT ALL ON accessdb.* TO nomal@'localhost'"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose < ./schema/create_table_member_list.sql
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose < ./schema/create_table_access_log.sql
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "LOAD DATA LOCAL INFILE '${DATA_TO_INSERT}' IGNORE INTO TABLE accessdb.member_list CHARACTER SET utf8 FIELDS TERMINATED BY ',' IGNORE 1 LINES"
echo "END"
