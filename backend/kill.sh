#!/bin/bash

for i in $(ps u | grep server.py | awk '{print $2;}'); do
	kill -9 "$i"
done
