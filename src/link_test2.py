from __future__ import division
import time
import paramiko
import subprocess


def initialize_logfile():
    if not os.path.exists('/tmp/browserlab/'):
        os.mkdir('/tmp/browserlab/')
    FILEOUT = open('/tmp/browserlab/logcmd.log', 'a+w')
    return FILEOUT

def logcmd(cmd, name, LOGFILE):
    LOGFILE.write(name + ': ' + str(time.time()) +': '+ cmd + '\n')
    print 'LOGFILE: '+ name + ': ' + str(time.time()) +': '+ cmd
    return

def try_command(cmd, client, server):
    busy = server.command(cmd)
    if (busy==0):
        client.command(cmd)
        return 0
    else:
        return -1

def fping():
    pass

 def tcpdump():
    pass

def kill():
    pass

def transferLogs():
    pass

