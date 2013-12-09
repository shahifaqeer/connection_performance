import paramiko
from collections import defaultdict
from constants import *
import time

# local server ssh parameters to authenticate
# make sure all systems (A, B, S, R) have been ssh-ed into by
# C at least once!

class RemoteHost:
  def __init__(self, ip, user, passwd, tcp_port, udp_port, name):
    # name can only be 'A', 'B', 'C', 'R', or 'S'
    self.name = name
    self.ip = ip
    self.user = user
    self.passwd = passwd
    self.tcp_port = tcp_port
    self.udp_port = udp_port

    self.host = self.connectHost(ip, user, passwd)

  def connectHost(self, ip, user, passwd):
    host = paramiko.SSHClient()
    host.load_system_host_keys()
    host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host.connect(ip, username=user, password=passwd)
    return host

  def check_connect(self):
    stdin, stdout, stderr = self.host.exec_command('ls /tmp/')
    for line in stdout:
      print 'check host: ' + line.strip('\n')
    return

  def remoteCommand(self, cmd, logfilename):
    """This should be used for starting iperf servers, pings,
    tcpdumps, etc.

    Commands issued here can be killed by cmd = 'killall <cmd>'"""
    if logfilename:
      cmd = cmd + ' >> testlogs/' + logfilename + ' &'
    stdin, stdout, stderr = self.host.exec_command(cmd)
    self.logcmd(cmd)
    return

  def startPingAll(self):
    self.remoteCommand('sh Browserlab/pings/pingall.sh &')
    return

  def stopPingAll(self):
    self.remoteCommand('killall ping')
    # self.remoteLogTransfer()

  def startIperfServer(self):
    if self.name == 'S':
      self.remoteCommand('ipef -s -p ')

# specific functions
  def createDataLogDir(self):
    """a server function only"""
    if self.name == 'S':
      foldername = str(time.localtimealtime()[0])+str(time.localtime()[1])+str(time.localtime()[2])
      self.remoteCommand('mkdir -p /home/gtnoise/data/'+foldername)
    return

  def remoteLogTransfer(self, srclog, dstdir):
    """Transfer all logfiles to homenetworklab/data/<DATE>/"""
    # TODO
    pass
    return
