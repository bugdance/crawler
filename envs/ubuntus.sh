#!/bin/bash

# ssh config
sudo useradd -r -m -s /bin/bash lolqq
sudo passwd lolqq
sudo vim /etc/ssh/sshd_config
PermitRootLogin no
MaxAuthTries 3
sudo systemctl restart sshd.service
# sudo
sudo chmod +w /etc/sudoers
sudo vim /etc/sudoers
root ALL=(ALL) ALL
lolqq ALL=(ALL) ALL
sudo chmod -w /etc/sudoers
# ufw
sudo ufw default deny
sudo ufw enable
sudo ufw allow 22
# sudo ufw allow ssh
# sudo ufw allow 22/tcp
# sudo ufw allow proto tcp from 192.168.0.1 to any port 22
# sudo ufw delete allow 22
# sudo ufw status
# sudo ufw disable

# sys update
sudo apt -y update
sudo apt -y upgrade
sudo rm -rf /var/lib/dpkg/lock*
# when error
cd /var/lib/dpkg
sudo mv info info.bak
sudo mkdir info
sudo apt -y upgrade

sudo apt -y install dos2unix lrzsz vim rsync wget curl make \
            gcc g++ openssl libssl-dev software-properties-common \
            apt-transport-https ca-certificates gnupg-agent \
            python-pip python-setuptools m2crypto shadowsocks \
            mongodb-clients mariadb-client redis-tools
            # python3.9-dev zlib1g-dev libffi-dev \
            # libbz2-dev liblzma-dev libmysqlclient-dev \

sudo apt -y install dos2unix lrzsz vim rsync wget curl make \
            gcc g++ openssl libssl-dev software-properties-common \
            apt-transport-https ca-certificates gnupg-agent

# cst
sudo tzselect
sudo ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# ping  0yes/1no
sudo sh -c "echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all"
# sudo sh -c "echo 0 > /proc/sys/net/ipv4/icmp_echo_ignore_all"
sudo vim /etc/sysctl.conf 中增加一行
net.ipv4.icmp_echo_ignore_all=1
sudo /sbin/sysctl -p

# docker
sudo apt -y remove docker docker-engine docker.io containerd runc
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"
sudo apt -y update
sudo apt -y install docker-ce docker-ce-cli containerd.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
# docker想要访问本机的外网IP, 把docker网段加进去
sudo ufw allow from 172.18.0.0/16 to any port 80

# https
sudo docker pull certbot/certbot

sudo docker run -it \
--name nginx-certbot -p 80:80 \
-v "/home/lolqq/webs/deploy/certbot.conf:/etc/nginx/nginx.conf" \
-d nginx

sudo docker run --rm -it \
--name certbot -p 80:80 \
-v "/etc/letsencrypt:/etc/letsencrypt" \
-v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
certbot/certbot certonly --agree-tos -d admin.lolqq.xyz \
-d api.lolqq.xyz -d preapi.lolqq.xyz -d tapi.lolqq.xyz -d dapi.lolqq.xyz


# # python39
# sudo wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz
# sudo tar xvf Python-3.9.6.tgz
# cd Python-3.9.6
# sudo ./configure && sudo make && sudo make install
# cd ..
# sudo pip3 install --upgrade pip
# sudo pip3 install -r requirements.txt
# # puppeteer
# sudo apt -y install ca-certificates fonts-liberation libappindicator3-1 \
#             libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 \
#             libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 \
#             libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
#             libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 \
#             libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 \
#             libxtst6 lsb-release xdg-utils
# sudo pyppeteer-install

# # command
# SET @@global.sql_mode= '';
# create database mcnadv default charset=utf8mb4;
# mysql --default-character-set=utf8mb4 -uroot -proot mcnadv < mcnadv.sql
# sudo find . -type f -exec dos2unix {} \;
# sudo kill -9 $(ps -ef | grep chrome | awk '{print $2}')
# sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
# sudo docker stop $(sudo docker ps -q) && sudo docker rm $(sudo docker ps -aq)
# sudo docker volume prune

# # mongodb
# sudo wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
# echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
# sudo apt -y update
# sudo apt -y install mongodb-org
# sudo systemctl start mongod.service
# sudo systemctl enable mongod.service

# # mariadb
# sudo apt -y install mariadb-server
# sudo /bin/cp -rf my_ubuntu.conf /etc/mysql/my.cnf
# sudo systemctl start mariadb.service
# sudo systemctl enable mariadb.service

# # redis
# sudo apt -y install redis-server
# sudo systemctl start redis.service
# sudo systemctl enable redis.service

# # nginx
# sudo apt -y install nginx
# sudo /bin/cp -rf nginx_ubuntu.conf /etc/nginx/nginx.conf
# sudo systemctl start nginx.service
# sudo systemctl enable nginx.service

# # node
# npm install -g typescript
# npm install -g create-react-app yarn
# create-react-app my-app
# npm start



# Poetry pybuilder Cookiecutter