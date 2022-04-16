#!/bin/bash
kill -9 `ps -ef | grep captcha_gun.py | awk '{print $2}' `
echo 3 > /proc/sys/vm/drop_caches
rm -rf captcha.log
gunicorn -c captcha_gun.py captcha_receive:app > /dev/null 2>&1 &
a
