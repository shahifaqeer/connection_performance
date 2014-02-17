import time
import paramiko
from link_constants import *


class Router:
  def __init__(self, ip, user, passwd):
    self.ip = ip
    self.user = user
    self.passwd = passwd

    self.host = self.connectHost(ip, user, passwd)

    self.host.remoteCommand('mkdir -p /tmp/browserlab/')
    self.fileout = open('/tmp/browserlab/logcmd.log', 'a+w')

  def connectHost(self, ip, user, passwd):
    host = paramiko.SSHClient()
    host.load_system_host_keys()
    host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print 'connect to ' + ip + ' user: ' + user + ' pass: ' + passwd
    if self.name!='S':
      host.connect(ip, username=user, password=passwd)
    else:
      host.connect(ip)
    return host

  def remoteCommand(self, cmd, logfilename=None, background=0):
    """This should be used for starting iperf servers, pings,
    tcpdumps, etc.

    Commands issued here can be killed by cmd = 'killall or pkill'"""
    if logfilename:
      cmd = cmd + ' >> /tmp/browserlab/' + logfilename
    if (background):
      cmd = cmd + ' &'
    #if sudo and self.name != 'R':
    #  cmd = 'echo "gtnoise" | sudo -S '+cmd

    stdin, stdout, stderr = self.host.exec_command(cmd)
    for line in stdout:
      print line

    self.logcmd(cmd)
    return

  def logcmd(self, cmd):
    self.fileout.write(self.name + ': ' + str(time.time()) +': '+ cmd + '\n')
    print self.name + ': ' + str(time.time()) +': '+ cmd + '\n'
    return

class LinkTest():
  def __init__(self):
    self.A = Host()
    self.R = Router()
    self.S = Server()
    return

  def iperfServer(self, proto):
    for remotehost in self.serverlist:
      if proto == 'udp':
        remotehost.remoteCommand('iperf -s -u -p '+str(remotehost.udp_port), 'iperf_'+remotehost.name+'_udp.log', 1)
      else:
        remotehost.remoteCommand('iperf -s -p '+str(remotehost.tcp_port), 'iperf_'+remotehost.name+'_tcp.log', 1)
    return

  def pingAll(self, interval, size_bytes):
    for remotehost in self.serverlist:
      list_of_ip = ""
      for remoteserver in self.serverlist:
        if remoteserver.name != remotehost.name:
          list_of_ip += remoteserver.ip + " "
      remotehost.remoteCommand('fping '+list_of_ip+' -p '+str(interval)+' -l -r 1 -A -b '+str(size_bytes), 'fping.log', 1 , 1)
    return

  def transferLogs(self, description):
    dst = self.S.createDataLogDir(description)

    for remotehost in [self.A, self.R]:
      remotedstdir = self.S.user+'@'+self.S.ip+':data/'+dst+'/'
      remotehost.remoteCommand('scp Browserlab/pings/*.log '+remotedstdir)
      remotehost.remoteCommand('scp testlogs/*.log '+remotedstdir)
      remotehost.remoteCommand('scp tcpdump/*.pcap '+remotedstdir)

    dstdir = 'data/'+dst+'/'
    self.S.remoteCommand('cp Browserlab/pings/*.log '+dstdir)
    self.S.remoteCommand('cp testlogs/*.log '+dstdir)
    self.S.remoteCommand('cp tcpdump/*.log '+dstdir)

    self.clearAllHosts()

    return
