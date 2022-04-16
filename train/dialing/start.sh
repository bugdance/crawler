#!/bin/bash

kill -9 `ps -ef | grep dial.py | awk '{print $2}' `
kill -9 `ps -ef | grep get.py | awk '{print $2}' `
echo 3 > /proc/sys/vm/drop_caches
rm -rf *.log
python3 get.py > /dev/null 2>&1 &
python3 dial.py > /dev/null 2>&1 &
#python3 check.py > /dev/null 2>&1 &