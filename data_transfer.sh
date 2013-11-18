#!/bin/bash

foldername='testlogs/bandwidth_tests4'
echo $foldername

mkdir -p $foldername

sshpass -p h0m3n3t scp root@192.168.142.1:testlogs/*test*.log $foldername

mv testlogs/*test4.log $foldername

#scp -r $foldername sarthak@riverside.noise.gatech.edu:Work/connection_performance/testlogs/
