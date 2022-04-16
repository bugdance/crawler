#!/bin/bash

kill -9 `ps -ef | grep chrome | awk '{print $2}' `
kill -9 `ps -ef | grep firefox | awk '{print $2}' `
kill -9 `ps -ef | grep geckodriver | awk '{print $2}' `
echo 3 > /proc/sys/vm/drop_caches
