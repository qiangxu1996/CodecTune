#!/usr/bin/env bash

# script_path="/home/rmw/sysbench-1.0/src/lua/"
script_path="/usr/share/sysbench/"

if [ "${1}" == "read" ]
then
    run_script=${script_path}"oltp_read_only.lua"
elif [ "${1}" == "write" ]
then
    run_script=${script_path}"oltp_write_only.lua"
else
    run_script=${script_path}"oltp_read_write.lua"
fi

sysbench ${run_script} \
        --mysql-host=$2 \
	--mysql-port=$3 \
	--mysql-user=root \
	--mysql-password=$4 \
	--mysql-db=sbtest \
	--db-driver=mysql \
        --mysql-storage-engine=innodb \
        --range-size=100 \
        --events=0 \
        --rand-type=uniform \
	--tables=8 \
	--table-size=1000000 \
	--report-interval=5 \
	--threads=3 \
	--time=$5 \
	run >> $6
