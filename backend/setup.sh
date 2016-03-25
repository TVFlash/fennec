#!/bin/bash

wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --user
python -m pip install -U pip --user flask
python -m pip install -U pip --user flask-cors
python -m pip install -U pip --user requests
python -m pip install -U pip --user websocket-server
python -m pip install -U pip --user isodate
