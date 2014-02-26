#SERVER
from __future__ import division
from datetime import datetime
import socket
import random
import subprocess
import threading
import os
import time

CLIENT_ADDRESS = 'localhost'
SERVER_ADDRESS = '130.207.97.240'
ROUTER_ADDRESS = '50.167.212.31'
port = 12345
backlog = 5
size = 1024
run_number = 100000
experiment_timeout = 10
transfer_timeout = experiment_timeout + 2
global BUSY


class SwitchFlag(threading.Thread):
    def run(self):
        print 'B = 1'
        BUSY = 1
        time.sleep(experiment_timeout + 5)
        print 'B = 0'
        BUSY = 0

class Command(object):
    def __init__(self, cmd):
        self.cmd = 'echo "hattorihanzo" | sudo -S ' + cmd
        self.process = None
        if not (os.path.exists('/tmp/browserlab/')):
            os.mkdir('/tmp/browserlab/')
        self.fout = open('/tmp/browserlab/debug.log', 'w')


    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        self.debug()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print self.process.returncode

    def debug(self):
        now = datetime.now()
        print str(now) +': '+ self.cmd
        self.fout.write(str(now) + ': ' + self.cmd + '\n')


def execute_command(msg):

    if not (os.path.exists('/tmp/browserlab/')):
        os.mkdir('/tmp/browserlab/')

    if 'CMD' in msg:
        if 'TIMEOUT' in msg:
            Command(msg['CMD']).run(msg['TIMEOUT'])
        else:
            Command(msg['CMD']).run(100)
        return 0
    else:
        print 'PROBLEM: no CMD in msg'
        return -1


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', port))
s.listen(backlog)
global BUSY
BUSY = 0

while 1:
    client, address = s.accept()
    print "Connection by ", address
    data = client.recv(size)
    if data:
        print data
        #print 'BUSY = ', BUSY
        BUSY = 0
        client.send(str(BUSY)+','+str(run_number))
        msg = eval(data)
        print 'execute command ', msg
        done = execute_command(msg)
        if 'START' in msg:
            run_number += msg['START']
        print 'Done: ', done
