from mytests import MyTestSuite
import time

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

def UDPBWGraphs(ctr_udp=1):
  mts = MyTestSuite()
  print "Connected to all hosts"
  mts.startAllPings()
  print "start pings"
  time_sleep = 10.0

  for k in range(ctr_udp):
    print "ROUND ", k
    for remoteclient in [mts.A, mts.B, mts.C, mts.R, mts.S]:
      for remoteserver in [mts.A, mts.B, mts.C, mts.R, mts.S]:
        if remoteserver != remoteclient:
          print (remoteclient.name + ' to ' + remoteserver.name)
          #mts.R.tcpDump('R_'+remoteclient.name+remoteserver.name+'.pcap')
          print 'start udpprobe test'
          bwlim = remoteclient.UDPProbeTest(remoteserver)
          print 'done udpprobe test; start iperf udp with bw '+bwlim
          #remoteclient.UDPIperfTest(remoteserver, bwlim)
          #print 'done iperf udp test'
          #mts.R.remoteCommand('killall tcpdump')
          # transfer logs
          #mts.transferLogs('traffic_'+remoteclient.name+remoteserver.name)
  mts.stopAllPings()
  #mts.transferLogs('udpbwtest')

  return mts

def UDPBWCompareProber(ctr_udp=1):
  mts = MyTestSuite()
  print "Connected to all hosts"

  remoteserver = mts.S
  remoterouter = mts.R
  for remoteclient in [mts.A, mts.B]: #, mts.C]:
    if remoteserver != remoteclient:
      for k in range(ctr_udp):
        print "ROUND ", k
        print ('UPLINK '+ remoteclient.name + ' to ' + remoteserver.name)
        bwlim = remoteclient.UDPProbeTest(remoterouter)
        bwlim = remoteclient.UDPProbeTest(remoteserver)
        bwlim = remoterouter.UDPProbeTest(remoteserver)
        print ('DOWNLINK '+ remoteserver.name + ' to ' + remoteclient.name)
        bwlim = remoterouter.UDPProbeTest(remoteclient)
        bwlim = remoteserver.UDPProbeTest(remoteclient)
        bwlim = remoteserver.UDPProbeTest(remoterouter)
      # transfer logs
      mts.transferLogs('udpprobe_'+remoteclient.name+remoteserver.name)
  return mts

def UDPBWCompareIperfTCP(ctr_tcp=1):
  mts = MyTestSuite()
  print "Connected to all hosts"
  print "start all tcp servers on all hosts"
  for x in [mts.A, mts.B, mts.C, mts.R, mts.S]:
    x.startIperfServer()
  remoteserver = mts.S
  remoterouter = mts.R
  for remoteclient in [mts.A, mts.B, mts.C]:
    if remoteserver != remoteclient:
      for k in range(ctr_tcp):
        print "ROUND ", k
        print ('UPLINK '+ remoteclient.name + ' to ' + remoteserver.name)
        bwlim = remoteclient.startIperfClient(remoterouter)
        bwlim = remoteclient.startIperfClient(remoteserver)
        bwlim = remoterouter.startIperfClient(remoteserver)
        print ('DOWNLINK '+ remoteserver.name + ' to ' + remoteclient.name)
        bwlim = remoterouter.startIperfClient(remoteclient)
        bwlim = remoteserver.startIperfClient(remoteclient)
        bwlim = remoteserver.startIperfClient(remoterouter)
      # transfer logs
      mts.transferLogs('iperftcp_'+remoteclient.name+remoteserver.name)
  return mts

def weirdLatencyTest(mts, ctr_tcp, ctr_udp, cong_host1, cong_host2, testtime, bwlim):
  mts.startAllPings()
  print "start pings"

  print "congestion udp traffic"
  mts.twoHostCongestion(cong_host1, cong_host2, 'udp', '7000', testtime, bwlim)
  mts.twoHostCongestion(cong_host2, cong_host1, 'udp', '7001', testtime, bwlim)

  if ctr_tcp > 0:
    mts.startIperfTCPServer()
    TCPTest(mts, ctr_tcp)
    print "iperf TCP x "+str(ctr_tcp)

  if ctr_udp > 0:
    mts.startIperfUDPServer()
    UDPTest(mts, ctr_udp)
    print "iperf UDP x "+str(ctr_udp)

  mts.stopAllPings()
  mts.killAll('iperf')
  mts.killAll('tcpdump')

  print "stop pings, kill iperf servers, and stop tcpdump"
  print  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " DONE"

  return mts

def UDPBWTests(ctr_udp):
  mts = MyTestSuite()
  mts.startAllPings()
  for remoteclient in [mts.A, mts.B, mts.C, mts.R, mts.S]:
    for remotesrcdirteserver in [mts.A, mts.B, mts.C, mts.R, mts.S]:
      if remoteserver != remoteclient:
        print (remoteclient.name + ' to ' + remoteserver.name)
        for k in range(ctr_udp):
          remoteclient.UDPProbeTest(remoteserver)
          time.sleep(time_sleep)
          # take a tcpdump at router between round 2 and 4
          mts.routerSmallTCPDump(remoteclient, remoteserver, k, 2, 4)

  mts.stopAllPings()
  return mts


def UDPProbeTests(ctr_udp=1):
  mts = MyTestSuite()
  time_sleep = 10.0
  for k in range(ctr_udp):
    print "ROUND ", k
    for remoteclient in [mts.A, mts.B, mts.C, mts.R, mts.S]:
      for remoteserver in [mts.A, mts.B, mts.C, mts.R, mts.S]:
        if remoteserver != remoteclient:
          print (remoteclient.name + ' to ' + remoteserver.name)
          mts.R.tcpDump('R_'+remoteclient.name+remoteserver.name+'.pcap')
          mts.startAllPings()
          print 'start test'
          remoteclient.UDPProbeTest(remoteserver)
          print 'done test'
          print 'no traffic for 10 secs'
          time.sleep(time_sleep)
          print 'done: stop all process and transfer logs'
          mts.stopAllPings()
          mts.R.remoteCommand('killall tcpdump')
          # transfer logs
          mts.transferLogs('traffic_'+remoteclient.name+remoteserver.name)
  return mts
