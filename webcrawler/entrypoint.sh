#!/bin/bash

service tor start
service privoxy start
nohup python3 /opt/run.py -f /opt/config/domains.yaml &

/bin/bash