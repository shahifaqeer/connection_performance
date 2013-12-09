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
    pass
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
      self.S.startIperfClient(self.R)
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
        self.S.startIperfClient(self.R, 'udp', bw)
        time.sleep(time_sleep)
    return

  def clearAllHosts():
    for host in self.serverList:
      host.allClear()
    return

def TCPTest(testsuite, counter):
  # counter around 50
  k = 0
  while k<counter:
    print 'TCP Round '+str(k)
    testsuite.startIperfShuffleTCP()
    k += 1
  # TODO copy iperf tcp files to server
  return

def UDPTest(testsuite, counter):
  # counter should be something like 10
  k = 0
  while k<counter:
    print 'UDP Round '+str(k)
    testsuite.startIperfShuffleUDP()
    k += 1
  # TODO copy iperf udp files to server
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
  print "\n DONE"
  return mts

