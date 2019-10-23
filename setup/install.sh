#!/bin/bash

apt update

echo "Setting up MySQL database..."

apt-get -y install mysql-server
service mysql start

mysql < "database-setup.sql"

echo "Setting up Python environment..."

apt-get -y install python3
apt -y install python3-pip

pip3 install importlib
pip3 install numpy
pip3 install mysql-connector
pip3 install JPype1
pip3 install Flask
pip3 install Flask-RESTful
pip3 install pycrypto

echo "Installing Java dependencies..."

apt -y install default-jre
mkdir -p ~/.jssc/linux
cp ./libjSSC-2.9_armhf.so ~/.jssc/linux

echo "PBRControl is ready to run!"

