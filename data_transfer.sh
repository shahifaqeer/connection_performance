#!/bin/bash

mv testlogs/*test*.log bandwidth_tests/

sshpass -p h0m3n3t scp root@192.168.142.1:/tmp/*test*.log bandwidth_tests/

scp -r bandwidth_tests sarthak@riverside.noise.gatech.edu:Work/connection_performance/
