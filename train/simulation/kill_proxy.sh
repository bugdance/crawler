#!/bin/bash

kill -9 `ps -ef | grep mitmdump | awk '{print $2}' `