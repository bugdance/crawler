#!/bin/bash

kill -9 `ps -ef | grep dial.py | awk '{print $2}' `
kill -9 `ps -ef | grep get.py | awk '{print $2}' `
kill -9 `ps -ef | grep check.py | awk '{print $2}' `
echo 3 > /proc/sys/vm/drop_caches