#!/bin/bash

kill -9 `ps -ef | grep gun.py | awk '{print $2}' `
echo 3 > /proc/sys/vm/drop_caches