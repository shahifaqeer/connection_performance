#!/usr/bin/python

from utils import RemoteHost
from constants import *
import time


class MyTestSuite():
  def __init__(self):
    # connect ALL hosts
    self.A = RemoteHost(A_ip, A_user, A_pass, A_port, A_udp, 'A')
    self.B = RemoteHost(B_ip, B_user, B_pass, B_port, B_udp, 'B')
    self.C = RemoteHost(C_ip, C_user, C_pass, C_port, C_udp, 'C')
    self.R = RemoteHost(R_ip, R_user, R_pass, R_port, R_udp, 'R')
    self.S = RemoteHost(S_ip, S_user, S_pass, S_port, S_udp, 'S')
    self.BWLIST = [50,100,150,200,500,600]
    self.serverList = [self.A, self.B, self.C, self.R, self.S]

  def startIperfServer(self):
    # start ALL iperf servers (already done for now locally)
    for remotehost in self.serverList:
      remotehost.remoteCommand('iperf -s -w 128k -p '+str(remotehost.tcp_port)+' >> /testlogs/iperf_'+remotehost.name+'_tcp.log &')
      remotehost.remoteCommand('iperf -s -u -w 128k -p '+str(remotehost.udp_port)+' >> /testlogs/iperf_'+remotehost.name+'_udp.log &')
    return

  def startAllPings(self):
    # start ALL pings
    self.A.startPingAll()
    self.B.startPingAll()
    self.C.startPingAll()
    self.R.startPingAll()
    self.S.startPingAll()
    return

  def stopAllPings(self):
    # stop ALL pings
    self.A.stopPingAll()
    self.B.stopPingAll()
    self.C.stopPingAll()
    self.R.stopPingAll()
    self.S.stopPingAll()
    return

  def killAll(self, cmd):
    self.A.remoteCommand("kill "+cmd)
    self.B.remoteCommand("kill "+cmd)
    self.C.remoteCommand("kill "+cmd)
    self.R.remoteCommand("kill "+cmd)
    self.S.remoteCommand("kill "+cmd)

  def startIperfShuffleTCP(self):
    # TODO downlink server to client is not working. S->R only
    # testsuite iperf tcp
    for server in self.serverList:
      if server.name != 'A':
        self.A.startIperfClient(server)
        time.sleep(time_sleep)
      if server.name != 'B':
        self.B.startIperfClient(server)
        time.sleep(time_sleep)
      if server.name != 'C':
        self.C.startIperfClient(server)
        time.sleep(time_sleep)
      if server.name != 'R':
        self.R.startIperfClient(server)
        time.sleep(time_sleep)
      if server.name != 'S':
        self.S.startIperfClient(server)
        time.sleep(time_sleep)
    return

  def startIperfShuffleUDP(self):
    # testsuite iperf udp
    for bw in self.BWLIST:
      for server in self.serverList:
        if server.name != 'A':
          self.A.startIperfClient(server, 'udp', bw)
          time.sleep(time_sleep)
        if server.name != 'B':
          self.B.startIperfClient(server, 'udp', bw)
          time.sleep(time_sleep)
        if server.name != 'C':
          self.C.startIperfClient(server, 'udp', bw)
          time.sleep(time_sleep)
        if server.name != 'R':
          self.R.startIperfClient(server, 'udp', bw)
          time.sleep(time_sleep)
        if server.name != 'S':
          self.S.startIperfClient(server, 'udp', bw)
          time.sleep(time_sleep)
    return

  def transferLogs(self, description):
    # create log directory on the server
    dst = self.S.createDataLogDir(description)

    # transfer for clients A, B, C
    for remotehost in [self.A, self.B, self.C]:
      remotedstdir = self.S.user+'@'+self.S.ip+':data/'+dst+'/'
      remotehost.remoteCommand('scp Browserlab/pings/*.log ' + remotedstdir)
      remotehost.remoteCommand('scp testlogs/*.log ' + remotedstdir)
      remotehost.remoteCommand('scp tcpdump/*.pcap ' + remotedstdir)

    dstdir = 'data/'+dst+'/'
    # transfer for R
    remotesrcdir = self.R.user+'@'+self.R.ip+':Browserlab/pings/*.log'
    self.S.remoteCommand('sshpass -p '+self.R.passwd+' scp '+remotesrcdir+' '+dstdir)
    remotesrcdir = self.R.user+'@'+self.R.ip+':testlogs/*.log'
    self.S.remoteCommand('sshpass -p '+self.R.passwd+' scp '+remotesrcdir+' '+dstdir)
    remotesrcdir = self.R.user+'@'+self.R.ip+':tcpdump/*.pcap'
    self.S.remoteCommand('sshpass -p '+self.R.passwd+' scp '+remotesrcdir+' '+dstdir)

    # transfer for S
    self.S.remoteCommand('cp Browserlab/pings/*.log '+dstdir)
    self.S.remoteCommand('cp testlogs/*.log '+dstdir)
    self.S.remoteCommand('cp tcpdump/*.pcap '+dstdir)

    # clear all logs
    # self.clearAllHosts()
    return

  def clearAllHosts(self):
    for remotehost in self.serverList:
      remotehost.allClear()
      # close all paramiko connections
      remotehost.host.close()
    return

  def twoHostCongestion(self,remoteclient, remoteserver, proto, port, testtime='10', bwlim='0'):
    server_cmd = 'iperf -s -p '+port+' -w 128k -i 2'
    client_cmd = 'iperf -c '+remoteserver.ip+' -p '+port+' -w 128k -i 2 -t '+testtime

    if proto == 'udp':
      server_cmd = server_cmd+' -u '
      client_cmd = client_cmd+' -u -b '+bwlim+'M '

    remoteserver.remoteCommand(server_cmd+' -f B -y C ', 'iperf_'+remoteclient.name+remoteserver.name+'_cong_server.log', 1)
    remoteclient.remoteCommand(client_cmd+' -f B -y C ', 'iperf_'+remoteclient.name+remoteserver.name+'_cong_client.log', 1)

    return


def TCPTest(testsuite, counter):
  # counter around 50
  k = 0
  while k<counter:
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'TCP Round '+str(k)
    testsuite.startIperfShuffleTCP()
    k += 1
  return

def UDPTest(testsuite, counter):
  # counter should be something like 10
  k = 0
  while k<counter:
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'UDP Round '+str(k)
    testsuite.startIperfShuffleUDP()
    k += 1
  return

def bandwidthTest(ctr_tcp, ctr_udp):
  mts = MyTestSuite()
  print "Connected to all hosts"
  mts.startAllPings()
  print "start pings"
  TCPTest(mts, ctr_tcp)
  print "iperf TCP x "+str(ctr_tcp)
  UDPTest(mts, ctr_udp)
  print "iperf UDP x "+str(ctr_udp)
  mts.stopAllPings()
  print "stop pings"
  print  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " DONE"
  return mts

def weirdLatencyTest(ctr_tcp, ctr_udp, cong_host1, cong_host2, bwlim):
  mts = MyTestSuite()
  print "Connected to all hosts"

  mts.startAllPings()
  print "start pings"

  # local C->A and A-> C udp traffic
  mts.twoHostCongestion(cong_host1, cong_host2, 'udp', '7000', '600', bwlim)
  mts.twoHostCongestion(cong_host2, cong_host1, 'udp', '7001', '600', bwlim)

  if ctr_tcp > 0:
    TCPTest(mts, ctr_tcp)
    print "iperf TCP x "+str(ctr_tcp)

  if ctr_udp > 0:
    UDPTest(mts, ctr_udp)
    print "iperf UDP x "+str(ctr_udp)

  mts.stopAllPings()

  print "stop pings"
  print  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " DONE"

  return mts
