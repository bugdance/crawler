#!/bin/bash
# base images python:3.9-slim-buster

# Docker -- base
sudo docker pull python:3.9-slim-buster
sudo docker run -it -d --name=python_base python:3.9-slim-buster
sudo docker exec -it python_base bash
# Apt
apt -y update
# Cst
tzselect
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# Clean
apt -y clean && apt -y autoclean
du -sh /var/cache/apt/
rm -rf /var/cache/apt/archives
history -c
# Package
sudo docker commit -a 'pyLeo' -m 'python39:base' python_base bugdancer/python39:base
sudo docker tag bugdancer/python39:base bugdancer/python39:base
sudo docker push bugdancer/python39:base

# Docker -- python39:base
sudo docker pull bugdancer/python39:base
sudo docker run -it -d --name=python_base bugdancer/python39:base
sudo docker exec -it python_base bash
# Opencv -- tasks
apt -y install libgl1-mesa-glx libglib2.0-dev
# Mysql -- webs
apt -y install gcc libmariadb-dev
# Puppeteer -- views
apt -y install ca-certificates fonts-liberation libappindicator3-1 \
        libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 \
        libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 \
        libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
        libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
        libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 \
        libxtst6 lsb-release xdg-utils
pyppeteer-install
# Pip
pip3 install -r require-{name}.txt
# Clean
apt -y clean && apt -y autoclean
du -sh /var/cache/apt/
rm -rf /var/cache/apt/archives
rm -rf ~/.cache/pip
history -c