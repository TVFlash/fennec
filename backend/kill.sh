#!/bin/bash

for i in $(ps u | grep chatserver.py | awk '{print $2;}'); do
	kill -9 "$i"
done
