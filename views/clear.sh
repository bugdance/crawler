#!/bin/bash

sudo kill -9 $(ps -ef | grep chrome | awk '{print $2}')
sudo sh -c "echo 1 > /proc/sys/vm/drop_caches"
sudo sh -c "echo 2 > /proc/sys/vm/drop_caches"
sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
sudo rm -rf *.log*
