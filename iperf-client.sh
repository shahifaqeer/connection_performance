#!/bin/bash
iperf -c 192.168.142.115 -p 5005 -y C -f B >> testlogs/iperfAS.log &
