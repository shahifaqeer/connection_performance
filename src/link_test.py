from utils import RemoteHost
import time
from link_constants import *

class LinkTest():
  def __init__(self):
    self.A = RemoteHost(A_ip, A_user, A_pass, A_port, A_udp, 'A')
    self.R = RemoteHost(R_ip, R_user, R_pass, R_port, R_udp, 'R')
    self.S = RemoteHost(S_ip, S_user, S_pass, S_port, S_udp, 'S')
    self.serverlist = [self.A, self.R, self.S]
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
