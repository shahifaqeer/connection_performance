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
  for remoteclient in [mts.A, mts.B]: #, mts.C]:
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

def TrafficLatencyTests(remoteclient, remoteserver, mts, ctr_tests=1):
  time_sleep = 10.0
  print "Connected to all hosts: Traffic Latency Test Start"

  print "start all tcp servers on all hosts"
  for x in [remoteclient, remoteserver]:
    x.startIperfServer()
  print "start all udp servers on all hosts"
  for x in [remoteclient, remoteserver]:
    x.startIperfServer('udp')

  for k in range(ctr_tests):
    print "ROUND ", k
    # start pings and router TCP dump
    print "start ping all pairs and tcpdump on R"
    mts.startAllPings(0.100)
    mts.R.tcpDump('R_'+remoteclient.name+remoteserver.name+'.pcap')
    #tcp dump on remoteclient and remoteserver too
    remoteclient.tcpDump(remoteclient.name+'_'+remoteclient.name+remoteserver.name+'.pcap')
    remoteserver.tcpDump(remoteserver.name+'_'+remoteclient.name+remoteserver.name+'.pcap')
    # no traffic for 10 sec - baseline
    time.sleep(time_sleep)
    # iperf tcp 10 sec client1 to S and vice versa
    print ('UPLINK tcp '+ remoteclient.name + ' to ' + remoteserver.name)
    bwlim = remoteclient.startIperfClient(remoteserver)
    print ('DOWNLINK tcp '+ remoteserver.name + ' to ' + remoteclient.name)
    bwlim = remoteserver.startIperfClient(remoteclient)
    # iperf udp 10 sec client1 to S and vice versa

    if remoteclient.name == 'B':
      bw = '15m'
    else:
      bw = '150m'

    print ('UPLINK udp '+ remoteclient.name + ' to ' + remoteserver.name)
    bwlim = remoteclient.startIperfClient(remoteserver, 'udp', bw)
    print ('DOWNLINK udp '+ remoteserver.name + ' to ' + remoteclient.name)
    bwlim = remoteserver.startIperfClient(remoteclient, 'udp', bw)

    # stop all pings, tcpdump, iperf servers
    mts.stopAllPings()
    mts.killAll('iperf')
    #killall tcpdumps
    mts.R.remoteCommand('killall tcpdump')
    remoteclient.remoteCommand('echo "gtnoise" | sudo -S killall tcpdump')
    remoteserver.remoteCommand('echo "gtnoise" | sudo -S killall tcpdump')
    # transfer logs
    mts.transferLogs('traffic_latency_'+remoteclient.name+remoteserver.name)

  return mts

def runTrafficLatTest(rate):
  mts = MyTestSuite()

  if rate != 0:
    mts.S.remoteCommand('echo "gtnoise" | sudo -S sh ratelimit.sh '+rate+'mbit '+rate+'mbit')
    mts.R.remoteCommand('sh ratelimit2.sh '+rate+'mbit '+rate+'mbit')
  else:
    mts.S.remoteCommand('echo "gtnoise" | sudo -S tc qdisc del dev eth1 root')
    mts.R.remoteCommand('tc qdisc del dev eth1 root')

  mts2 = TrafficLatencyTests(mts.A, mts.S, mts)
  mts2 = TrafficLatencyTests(mts.B, mts.S, mts)
  mts2 = TrafficLatencyTests(mts.C, mts.S, mts)

  return

def startARound(mts, round_num, scenario=None, remoteclient=None, remoteserver=None):
  mts.startAllPings(0.100)
  mts.R.tcpDump('R.pcap')
  if scenario is not None:
    #tcp dump on remoteclient and remoteserver too
    remoteclient.tcpDump(remoteclient.name+'.pcap')
    remoteserver.tcpDump(remoteserver.name+'.pcap')
  mts.wirelessQualityLog()
  return

def endARound(mts, round_num, description, scenario=None, remoteclient=None, remoteserver=None):
  time_wait = 5.0
  mts.stopAllPings()
  mts.R.remoteCommand('killall tcpdump')
  if scenario is not None:
    remoteclient.remoteCommand('echo "gtnoise" | sudo -S killall tcpdump')
    remoteserver.remoteCommand('echo "gtnoise" | sudo -S killall tcpdump')
  mts.transferLogs(description)
  #wait for 5 seconds due to transfers before next round begins
  time.sleep(time_wait)
  return


def TCPLatencyTest(mts, rate, num_of_rounds=1):
  rate = str(rate)
  time_notraffic = 10.0

  print "start all tcp servers on all hosts"
  for x in mts.serverList:
    x.startIperfServer()

  k = 0

  for ctr in range(num_of_rounds):
    print "ROUND ", ctr
    des = 'traffic_no_'+rate+'mbit'
    print k, des
    startARound(mts, k)
    time.sleep(time_notraffic)
    endARound(mts, k, des)

    remoteserver = mts.S
    for remoteclient in [mts.A, mts.B, mts.C]:
      k+=1
      des =  'traffic_'+remoteclient.name+'S_'+rate+'mbit'
      print k, des
      startARound(mts, k, des, remoteclient, remoteserver)
      bwlim = remoteclient.startIperfClient(remoteserver)
      endARound(mts, k, des, des, remoteclient, remoteserver)

      k+=1
      des = 'traffic_S'+remoteclient.name+'_'+rate+'mbit'
      print k, des
      startARound(mts, k, des, remoteclient, remoteserver)
      bwlim = remoteserver.startIperfClient(remoteclient)
      endARound(mts, k, des, des, remoteclient, remoteserver)

  return mts

def runTCPLatTest(rate):
  mts = MyTestSuite()
  #buffersize = str(buffersize) #in kb

  if rate != 0:
    rate = str(rate)
    mts.Q.remoteCommand('sh ratelimit3.sh eth0 '+rate)
    mts.Q.remoteCommand('sh ratelimit3.sh eth1 '+rate)
    #mts.Q.remoteCommand('sh ratelimit2.sh eth0 '+rate+' '+rate+' '+buffersize)
    #mts.Q.remoteCommand('sh ratelimit2.sh eth1 '+rate+' '+rate+' '+buffersize)
    #mts.R.remoteCommand('sh ratelimit2.sh eth1 '+rate+'mbit '+rate+'mbit')
  else:
    mts.Q.remoteCommand('tc qdisc del dev eth0 root')
    mts.Q.remoteCommand('tc qdisc del dev eth1 root')
    #mts.R.remoteCommand('tc qdisc del dev eth1 root')

  mts2 = TCPLatencyTest(mts, rate)
  mts2.stop_n_clear()
  mts2.closeAllHosts()

  return
