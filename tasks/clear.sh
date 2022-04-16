#!/bin/bash

sudo sh -c "echo 1 > /proc/sys/vm/drop_caches"
sudo sh -c "echo 2 > /proc/sys/vm/drop_caches"
sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
sudo rm -rf *.log*
sudo rm -rf logs
sudo mkdir logs
sudo chmod -R 777 *
