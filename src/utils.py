import paramiko
from collections import defaultdict
from constants import *
import time

# local server ssh parameters to authenticate
# make sure all systems (A, B, S, R) have been ssh-ed into by
# C at least once!
def connectHost(ip, user, passwd):
  host = paramiko.SSHClient()
  host.load_system_host_keys()
  host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  host.connect(ip, username=user, password=passwd)
  return host

def check_connect(host):
  stdin, stdout, stderr = host.exec_command('ls /tmp/')
  for line in stdout:
    print 'check host: ' + line.strip('\n')
  return

def remoteCommand(host, cmd, logfilename):
  """This should be used for starting iperf servers, pings,
  tcpdumps, etc.

  Commands issued here can be killed by cmd = 'killall <cmd>'"""
  if logfilename:
    cmd = cmd + ' >> testlogs/' + logfilename + ' &'
  stdin, stdout, stderr = host.exec_command(cmd)
  logcmd(cmd)
  return

# specific functions
def createDataLogDir(server):
  """a server function only"""
  foldername = str(time.localtimealtime()[0])+str(time.localtime()[1])+str(time.localtime()[2])
  remoteCommand(server, 'mkdir -p /home/gtnoise/data/'+foldername)
  return

def remoteLogTransfer(host, logfilename):
  """Transfer all logfiles to homenetworklab/data/<DATE>/"""
