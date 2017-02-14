#!/bin/sh
apt-get -y update
apt-get -y install python3-pip
apt-get -y install python-pip
pip install supervisor
pip3 install -r requirements.txt