#SERVER
from __future__ import division

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


CMD = {}
TIMEOUT = {}

CMD['tcpdump'] = Command('tcpdump -s 100 -i any -w /tmp/browserlab/S.pcap')
CMD['fping'] = Command('fping '+ROUTER_ADDRESS+' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/ping_S.log')
CMD['iperf_tcp_server'] = Command('iperf -s -i 0.5 >> /tmp/browserlab/AS_iperf_tcp_S.log')
CMD['iperf_tcp_server_rev'] = Command('iperf -s -i 0.5 -t '+ str(experiment_timeout) +' --reverse >> /tmp/browserlab/SA_iperf_tcp_S.log')
CMD['iperf_tcp_client'] = Command('iperf -c '+CLIENT_ADDRESS+' -i 0.5 -t ' + str(experiment_timeout) + ' >> /tmp/browserlab/SR_iperf_tcp_S.log')
CMD['make_transfer_directory'] = Command('mkdir -p /home/sarthak/Desktop/logs/'+str(run_number))
CMD['transfer_logs'] = Command('sleep '+str(transfer_timeout)+'; cp /tmp/browserlab/*.log /home/sarthak/Desktop/logs/'+str(run_number))
CMD['transfer_pcaps'] = Command('sleep '+str(transfer_timeout)+'; cp /tmp/browserlab/*.pcap /home/sarthak/Desktop/logs/'+str(run_number))

TIMEOUT['tcpdump'] = experiment_timeout + 1
TIMEOUT['fping'] = experiment_timeout
TIMEOUT['iperf_tcp_server'] = experiment_timeout
TIMEOUT['iperf_tcp_server_rev'] = experiment_timeout
TIMEOUT['iperf_tcp_client'] = experiment_timeout
TIMEOUT['make_transfer_directory'] = experiment_timeout
TIMEOUT['transfer_logs'] = experiment_timeout + 2
TIMEOUT['transfer_pcaps'] = experiment_timeout + 2

def execute_command(msg):
# msg = ['tcpdump', 'fping', ... ]
    B = SwitchFlag()
    B.start()

    if not (os.path.exists('/tmp/browserlab/')):
        os.mkdir('/tmp/browserlab/')

    for cmd_name in msg:
        CMD[cmd_name].run(TIMEOUT[cmd_name])

    return 0


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
        print 'BUSY = ', BUSY
        client.send(str(BUSY)+','+str(run_number))
        # not busy
        if BUSY == 0:
            msg = eval(data)
            #msg = data.split(',')
            print 'execute command ', msg
            BUSY = 1
            done = execute_command(msg)
            run_number += 1
            # start executing command here
            # command should be non blocking
            # after its over set BUSY = 0 automatically
            print 'Done: ', done
