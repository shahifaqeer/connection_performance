from __future__ import division
from datetime import datetime
from commands import *
from random import randint

import time
import socket
import schedule
import os
import paramiko
import threading
import subprocess
import shlex
import subprocess


CONTROL_PORT = 12345
MSG_SIZE = 1024
global run_number

experiment_timeout =  10
transfer_timeout =  experiment_timeout + 2
run_number =100000
ROUTER_ADDRESS_LOCAL = '192.168.1.1'
ROUTER_USER = 'root'
ROUTER_PASS = 'bismark123'
ROUTER_ADDRESS_GLOBAL =  '50.167.212.31'
SERVER_ADDRESS = '130.207.97.240'
CLIENT_ADDRESS = '192.168.1.153'
CLIENT_WIRELESS_INTERFACE_NAME = 'wlan0'
ROUTER_WIRELESS_INTERFACE_NAME = 'wlan0'

# client commands
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.fout = initialize_logfile()

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
        now = time.time()
        print str(now) +': '+ self.cmd
        self.fout.write(str(now) + ': ' + self.cmd + '\n')


def initialize_logfile():
    if not os.path.exists('/tmp/browserlab/'):
        os.mkdir('/tmp/browserlab/')
    fileout = open('/tmp/browserlab/logcmd.debug', 'a+w')
    return fileout

def logcmd(cmd, name, logfile):
    logfile.write(name + ': ' + str(time.time()) +': '+ cmd + '\n')
    print 'DEBUG: '+ name + ': ' + str(time.time()) +': '+ cmd
    return


class Router:
    def __init__(self, ip, user, passwd):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.name = 'R'
        self.logfile = initialize_logfile()
        self.server = SERVER_ADDRESS
        self.client = CLIENT_ADDRESS
        self.router = ROUTER_ADDRESS_LOCAL
        self.host = self.connectHost(ip, user, passwd)
        self.remoteCommand('mkdir -p /tmp/browserlab/')
        #self.initialize_servers()

    def connectHost(self, ip, user, passwd):
        host = paramiko.SSHClient()
        host.load_system_host_keys()
        host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print 'DEBUG: connect to ' + ip + ' user: ' + user + ' pass: ' + passwd
        host.connect(ip, username=user, password=passwd)
        return host

    def remoteCommand(self, cmd):
        """This should be used for starting iperf servers, pings,
        tcpdumps, etc.
        """
        stdin, stdout, stderr = self.host.exec_command(cmd)
        for line in stdout:
            print 'DEBUG: '+ line
        return

    def initialize_servers(self):
        # iperf tcp serverip
        self.remoteCommand('iperf -s >> ' + self.name + '_iperf_tcp_server.log &')
        # iperf udp server
        self.remoteCommand('iperf -s -u >> '+ self.name + '_iperf_udp_server.log &')
        # udp probe server
        self.remoteCommand('udpprobeserver >> ' + self.name + '_udpprobe_server.log &')
        return 0

    def command(self, cmd):
        self.remoteCommand(cmd['CMD'])
        logcmd(cmd, self.name, self.logfile)
        return


class Client:
    def __init__(self, ip):
        self.name = 'A'
        self.ip = ip
        self.logfile = initialize_logfile()

    def command(self, cmd):
        if not ('TIMEOUT' in cmd):
            if 'STDOUT' in cmd:
                outfile = open(cmd['STDOUT'], 'a+w')
            else:
                outfile = None
            #use subprocess for immediate command
            p = subprocess.call(cmd['CMD'], stdout = outfile, shell = True)
        else:
            Command(cmd['CMD']).run(cmd['TIMEOUT'])
        logcmd(cmd['CMD'], self.name, self.logfile)
        return

    def fping(self, list_of_IPs=None):
        if list_of_IPs is None:
            y = ROUTER_ADDRESS_LOCAL+' '+ SERVER_ADDRESS
        else:
            y = ''
            for x in list_of_IPs:
                y = y + x + ' '
        self.command({'CMD':'fping '+ y +' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_A.log',
                   'TIMEOUT': experiment_timeout})
        return

    def tcpdump(self):
        return

    def radiotapdump(self):
        return

    def iperf_tcp_server(self):
        return

    def iperf_tcp_client(self):
        return

    def iperf_tcp_client_reverse(self):
        return

    def killall(self):
        return

    def transfer_logs(self):
        return


class Server:
    def __init__(self, ip):
        self.name = 'S'
        self.ip = ip
        self.logfile = initialize_logfile()

    def command(self, cmd):
        if type(cmd) is dict:
            msg = str(cmd)  #remember to eval and check for flags on other end (START, TIMEOUT, CMD, SUDO(?))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_ADDRESS, CONTROL_PORT))
        s.send(msg)
        response = s.recv(MSG_SIZE)
        print 'RECEIVED ', response
        s.close()
        res, run_num, pid = response.split(',')
        logcmd(msg, self.name, self.logfile)
        return int(res), int(run_num), pid


class Devices:
    def __init__(self):
        self.A = Client(CLIENT_ADDRESS)
        self.R = Router(ROUTER_ADDRESS_LOCAL, ROUTER_USER, ROUTER_PASS)
        self.S = Server(SERVER_ADDRESS)
        self.device_list = [self.A, self.R, self.S]

    def test_function(self):
        cmd = raw_input("Enter a command for all devices: ")
        for dev in self.device_list:
            dev.command(cmd)
        return


def test_cmd(dev, cmd):
    dev.command(cmd)
    return



def experiment(S,R,C, exp):
    print "only fpings no traffic for 10 sec"
    run_number = pings_and_tcpdump(S,R,C)
    radiotap_dump([R,C])
    # run experiment here
    experiment_comment = exp()

    print 'wait for 12 sec for completion else send kill'
    time.sleep(experiment_timeout+2)
    kill_and_transfer(S,R,C, run_number, experiment_comment)
    return 0


class Experiment:
    def __init__:
        self.A = Client(CLIENT_ADDRESS)
        self.R = Router(ROUTER_ADDRESS_LOCAL, ROUTER_USER, ROUTER_PASS)
        self.S = Server(SERVER_ADDRESS)
        self.device_list = [self.A, self.R, self.S]
        self.run_number = 0

    def create_monitor_interface(self):
        self.A.command({'CMD': 'iw dev '+ CLIENT_WIRELESS_INTERFACE_NAME +' interface add mon0 type monitor flags none'})
        self.R.command({'CMD': 'iw dev '+ ROUTER_WIRELESS_INTERFACE_NAME +' interface add mon0 type monitor flags none'})
        self.A.command({'CMD': 'ifconfig mon0 up'})
        self.R.command({'CMD': 'ifconfig mon0 up'})
        return 0

    def radiotap_dump(self):
        self.create_monitor_interface()
        self.A.command({'CMD':'tcpdump -i mon0 -s 65000 -p -U -w /tmp/fishing.dump - G' + str(experiment_timeout), 'TIMEOUT':experiment_timeout})
        self.R.command({'CMD':'tcpdump -i mon0 -s 65000 -p -U -w /tmp/fishing.dump - G' + str(experiment_timeout), 'TIMEOUT':experiment_timeout})

    def ping_all(self):
        s, run_number, pid = self.S.command({'CMD':'fping '+ROUTER_ADDRESS_GLOBAL+' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_S.log',
                                    'TIMEOUT': experiment_timeout, 'START':1, 'SUDO':1})
        self.run_number = run_number

        self.A.command({'CMD':'fping '+ROUTER_ADDRESS_LOCAL+' '+ SERVER_ADDRESS +' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_A.log',
                    'TIMEOUT': experiment_timeout})
        self.R.command({'CMD':'fping '+CLIENT_ADDRESS+' '+ SERVER_ADDRESS +' -p 100 -c '+ str(experiment_timeout * 10) + ' -r 1 -A >> /tmp/browserlab/fping_R.log &'})
        return

    def tcpdump_all(self):
        self.S.command({'CMD':'tcpdump -s 100 -i any -w /tmp/browserlab/S.pcap -G 10', 'TIMEOUT':experiment_timeout, 'SUDO':1})
        self.A.command({'CMD':'tcpdump -s 100 -i any -w /tmp/browserlab/A.pcap', 'TIMEOUT':experiment_timeout})
        self.R.command({'CMD':'tcpdump -s 100 -i any -w /tmp/browserlab/R.pcap &'})
        return

    def kill_all(self)
        self.S.command({'CMD':'killall fping', 'SUDO': 1}) #should be done with pid instead
        self.S.command({'CMD':'killall tcpdump', 'SUDO': 1})
        self.S.command({'CMD':'killall iperf', 'SUDO': 1})

        self.A.command({'CMD':'killall fping'}) #should be done with pid instead
        self.A.command({'CMD':'killall tcpdump'})
        self.A.command({'CMD':'killall iperf'})

        self.R.command({'CMD':'killall fping'}) #should be done with pid instead
        self.R.command({'CMD':'killall tcpdump'})
        self.R.command({'CMD':'killall iperf'})
        return

    def transfer_logs(self, run_number, comment):
        self.S.command({'CMD': 'mkdir -p /home/sarthak/Desktop/logs/'+str(run_number)+'_'+comment})
        self.S.command({'CMD':'cp /tmp/browserlab/*.log /home/sarthak/Desktop/logs/'+str(run_number)+'_'+comment})
        self.S.command({'CMD':'cp /tmp/browserlab/*.pcap /home/sarthak/Desktop/logs/'+str(run_number)+'_'+comment})

        self.A.command({'CMD': 'mkdir -p /tmp/browserlab/'+str(run_number)+'_'+comment}) # instead of time use blocking resource to sync properly
        self.A.command({'CMD':'cp /tmp/browserlab/*.log /tmp/browserlab/'+str(run_number)+'_'+comment+'/'})
        self.A.command({'CMD':'cp /tmp/browserlab/*.pcap /tmp/browserlab/'+str(run_number)+'_'+comment+'/'})

        self.A.command({'CMD':'sshpass -p '+ ROUTER_PASS +' scp '+ ROUTER_USER + '@' + ROUTER_ADDRESS_LOCAL + ':/tmp/browserlab/* /tmp/browserlab/'+str(run_number)+'_'+comment+'/'})

        self.R.command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        self.R.command({'CMD':'rm -rf /tmp/browserlab/*.log'})
        self.A.command({'CMD':'rm -rf /tmp/browserlab/*.pcap'})
        self.A.command({'CMD':'rm -rf /tmp/browserlab/*.log'})
        self.S.command({'CMD':'rm -rf /tmp/browserlab/*.pcap', 'SUDO':1})
        self.S.command({'CMD':'rm -rf /tmp/browserlab/*.log', 'SUDO':1})

        # TODO gzip folder /tmp/browserlab/run_number and transfer it?

        return

    def run_experiment(self, exp):
        self.ping_all()
        self.tcpdump_all()

        comment = exp()

        time.sleep(experiment_timeout+2)
        self.kill_all()
        self.transfer_logs(self.run_number, comment)
        return

    # EXPERIMENTS
    # passed as args into run_experiment()
    def no_traffic(self):
        return 'no_tra'

    def iperf_tcp_up_AR(self):
        self.R.command('iperf -s -y C >> /tmp/browserlab/iperf_AR_R.log &')
        self.A.command('iperf -c ' + ROUTER_ADDRESS_LOCAL + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AR_A.log &')
        return 'AR_tcp'
    return 0

    def iperf_tcp_dw_RA(self):
        A.command('iperf -s -y C >> /tmp/browserlab/iperf_RA_A.log &')
        R.command('iperf -c ' + CLIENT_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_RA_R.log &')
        return 'RA_tcp'

    def iperf_tcp_up_RS(self):
        S.command('iperf -s -y C >> /tmp/browserlab/iperf_RS_S.log &')
        R.command('iperf -c ' + SERVER_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AR_A.log &')
        return 'RS_tcp'

    def iperf_tcp_dw_SR(self):
        A.command('iperf -s -y C >> /tmp/browserlab/iperf_RA_A.log &')
        A.command('iperf -c ' + CLIENT_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_RA_R.log &')
        return 'SR_tcp'

    def iperf_tcp_up_AS(S,R,C):
        R.command('iperf -s -y C >> /tmp/browserlab/iperf_AR_R.log &')
        A.command('iperf -c ' + ROUTER_ADDRESS_LOCAL + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AR_A.log &')
        return 'AS_tcp'

    def iperf_tcp_dw_SA(S,R,C):
        A.command('iperf -s -y C >> /tmp/browserlab/iperf_RA_A.log &')
        A.command('iperf -c ' + CLIENT_ADDRESS + ' -y C -i 0.5 >> /tmp/browserlab/iperf_RA_R.log &')
        return 'SA_tcp'

    # udpprobe gives both up and dw
    def probe_udp_AR(S,R,C):
        R.command('iperf -s -y C >> /tmp/browserlab/iperf_AR_R.log &')
        A.command('iperf -c ' + ROUTER_ADDRESS_LOCAL + ' -y C -i 0.5 >> /tmp/browserlab/iperf_AR_A.log &')
    return 'AR_udp'

    def probe_udp_RS(S,R,C):
    return 'RS_udp'

    def probe_udp_AS(S,R,C):
    return 'AS_udp'
