#CLIENT
from __future__ import division
from datetime import datetime

import time
import socket
import schedule
import os
from random import randint

SERVER_ADDRESS = 'localhost'
CONTROL_PORT = 12345
MSG_SIZE = 1024
global run_number

experiment_timeout =  10
transfer_timeout =  experiment_timeout + 2
run_number =100000
ROUTER_ADDRESS = '192.168.1.1'
ROUTER_ADDRESS_GLOBAL =  '50.167.212.31'
SERVER_ADDRESS = '130.207.97.240'

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print self.process.returncode



def send_command(msg):
    if type(msg) is dict:
        msg = str(msg)  #remember to eval and check for flags on other end (START, TIMEOUT, CMD, SUDO(?))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_ADDRESS, CONTROL_PORT))
    s.send(msg)
    response = s.recv(MSG_SIZE)
    print 'RECEIVED ', response
    s.close()
    res, run_num = response.split(',')
    return int(res), int(run_num)

if __name__ == "__main__":

    #schedule.every(1).minutes.do(experiment)

    if True:
    #   schedule.run_pending()
        print "try running fping"
        msg = {}
        msg['CMD'] = 'fping '+ROUTER_ADDRESS_GLOBAL+' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_S.log'
        msg['TIMEOUT'] = experiment_timeout
        msg['START'] = 1
        s, run_number = send_command(msg)

        msg['CMD'] = 'tcpdump -s 100 -i any -w /tmp/browserlab/S.pcap'
        msg['START'] = 0
        send_command(msg)

        print 'wait for 15 sec for completion else send kill'
        time.sleep(15.0)

        send_command({'CMD':'killall fping'})
        send_command({'CMD': 'mkdir -p /home/sarthak/Desktop/logs/'+str(run_number)})
        send_command({'CMD':'cp /tmp/browserlab/*.log /home/sarthak/Desktop/logs/'+str(run_number)})
        send_command({'CMD':'cp /tmp/browserlab/*.pcap /home/sarthak/Desktop/logs/'+str(run_number)})
        send_command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        send_command({'CMD':'rm -rf /tmp/browserlab/*.log'})

        print 'DONE sleep for 10 sec'
        time.sleep(10)
