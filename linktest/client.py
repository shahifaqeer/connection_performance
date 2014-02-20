#CLIENT
from __future__ import division
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

CMD = {}
TIMEOUT = {}

CMD['tcpdump'] = Command('tcpdump -s 100 -i any -w /tmp/browserlab/S.pcap')
CMD['fping'] = Command('fping '+ROUTER_ADDRESS+' '+ SERVER_ADDRESS +'-p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/ping_A.log')
CMD['iperf_tcp_server'] = Command('iperf -c ' + SERVER_ADDRESS + ' -i 0.5 >> /tmp/browserlab/AS_iperf_tcp_A.log')
CMD['iperf_tcp_server_rev'] = Command('iperf -c '+ SERVER_ADDRESS+' -i 0.5 -t '+ str(experiment_timeout) +' --reverse >> /tmp/browserlab/SA_iperf_tcp_A.log')
CMD['iperf_tcp_client'] = Command('iperf -s -i 0.5  >> /tmp/browserlab/RA_iperf_tcp_A.log')
CMD['make_transfer_directory'] = Command('mkdir -p /tmp/browserlab/logs/'+str(run_number))
CMD['transfer_logs'] = Command('sleep '+str(transfer_timeout)+'; cp /tmp/browserlab/*.log /tmp/browserlab/logs/'+str(run_number))
CMD['transfer_pcaps'] = Command('sleep '+str(transfer_timeout)+'; cp /tmp/browserlab/*.pcap /tmp/browserlab/logs/'+str(run_number))

TIMEOUT['tcpdump'] = experiment_timeout + 1
TIMEOUT['fping'] = experiment_timeout
TIMEOUT['iperf_tcp_server'] = experiment_timeout
TIMEOUT['iperf_tcp_server_rev'] = experiment_timeout
TIMEOUT['iperf_tcp_client'] = experiment_timeout
TIMEOUT['make_transfer_directory'] = experiment_timeout
TIMEOUT['transfer_logs'] = experiment_timeout + 2
TIMEOUT['transfer_pcaps'] = experiment_timeout + 2

'''
def iperf_tcp_AS:
    res = server.command('iperf -s -i 0.5 >> S_iperf_tcp_AS.log &')
    if res == 0:
        client.command('iperf -c '+server.ip+' -i 0.5 -t 5 >> A_iperf_tcp_AS.log &')
        return 0
    return -1

def iperf_tcp_SA:
    return

def iperf_tcp_AR:
    return

def iperf_tcp_RA:
    return

def iperf_tcp_RS:
    return

def iperf_tcp_SR:
    return

def fping():
    return

def tcpdump():
    return

'''

def send_command(msg):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_ADDRESS, CONTROL_PORT))
    s.send(msg)
    response = s.recv(MSG_SIZE)
    print 'RECEIVED ', response
    s.close()
    res, run_num = response.split(',')
    return int(res), int(run_num)


def experiment(msg):
    timeout = 1
    while timeout > 0:
        time.sleep(timeout)
        server_busy, run_number = send_command(str(msg))
        if server_busy == 0:
            #execute commands on client
            return 0
        timeout = randint(0,30)

def execute_command(msg):
# msg = ['tcpdump', 'fping', ... ]
    if not (os.path.exists('/tmp/browserlab/')):
        os.mkdir('/tmp/browserlab/')

    for cmd_name in msg:
        CMD[cmd_name].run(TIMEOUT[cmd_name])

    return 0


if __name__ == "__main__":

    #schedule.every(1).minutes.do(experiment)

    while True:
    #   schedule.run_pending()
        experiment(['fping', 'iperf_tcp_server', 'make_transfer_directory', 'transfer_logs', 'transfer_pcaps'])
        print "try running experiment"
        #time.sleep(10)
