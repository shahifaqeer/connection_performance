import paramiko
#from collections import defaultdict
#from constants import *
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

    self.fileout = open('testlogs/logcmd.log', 'a+w')

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

  def check_connect(self):
    stdin, stdout, stderr = self.host.exec_command('ls /tmp/')
    for line in stdout:
      print 'check host: ' + line.strip('\n')
    return

  def remoteCommand(self, cmd, logfilename=None, background=0):
    """This should be used for starting iperf servers, pings,
    tcpdumps, etc.

    Commands issued here can be killed by cmd = 'killall <cmd>'"""
    if logfilename:
      cmd = cmd + ' >> testlogs/' + logfilename
    if (background):
      cmd = cmd + ' &'

    stdin, stdout, stderr = self.host.exec_command(cmd)
    for line in stdout:
      print line

    self.logcmd(cmd)
    return

  def startPingAll(self):
    if self.name == 'R':
      self.remoteCommand('sh Browserlab/pings/pingall.sh')
    else:
      self.remoteCommand('sh Browserlab/pings/pingall.sh "' + self.name + '"')
    return

  def stopPingAll(self):
    self.remoteCommand('killall ping')
    # self.remoteLogTransfer()

  def startIperfServer(self):
    cmd = 'iperf -s -p '+str(self.tcp_port)
    logfilename = 'iperf_tcp_server_'+self.name+'.log'
    sin, sout, serr = self.host.exec_command(cmd + ' >> ' + logfilename + ' &')
    return

  def startIperfClient(self, server, proto='tcp', bwlim=0, reverse=0):
    """(server, proto, bwlim) where server is a RemoteHost object, proto
    is 'udp' or 'tcp' (default) and bwlim is a num is M"""

    if proto == 'udp':
      cmd = 'iperf -p '+str(server.udp_port)+ ' -c '+str(server.ip)+' -u -b '+str(bwlim)+'M -y C -f B -i 1 '
      logfilename = 'iperf_'+self.name+server.name+'_'+proto+str(bwlim)+'.log'
    else:
      cmd = 'iperf -p '+str(server.tcp_port)+ ' -c '+str(server.ip)+' -y C -f B -i 1 '
      logfilename = 'iperf_'+self.name+server.name+'.log'

    if (reverse):
      cmd = cmd + ' -r'

    self.remoteCommand(cmd, logfilename)
    return

  def UDPProbeTest(self, server):
    sin, sout, serr = server.host.exec_command('udpprobeserver &')
    cmd = 'udpprober -s '+server.ip
    logfilename = 'udpprobe_'+self.name+server.name+'.log'
    #self.remoteCommand(cmd, logfilename)
    bwlim = 1000000
    sin, sout, serr = self.host.exec_command(cmd)
    for line in sout:
      self.remoteCommand('echo '+line.split('\n')[0], logfilename)
      bwlim = line.split(',')[2]
    #fcap = open('testlogs/'+logfilename, 'r')
    #stats = fcap.readline().split(',')
    return str(bwlim)

  def UDPIperfTest(self, server, bwlim):
  print "start all tcp servers on all hosts"
  for x in [mts.A, mts.B, mts.C, mts.R, mts.S]:
    x.startIperfServer()
    #sin, sout, serr = server.host.exec_command('iperf -s -u &')
    #start udp servers manually
    servip = server.ip
    # weird problem: udp iperf to router from clients works only on 192.168.10.1
    # whereas from server works only on 192.168.20.2
    if (server.name == 'R') and (self.name != 'S'):
      servip = '192.168.10.1'
    cmd = 'iperf -c '+servip+' -u -b '+bwlim+'k'+' -y C'
    logfilename = 'iperf_udp_'+self.name+server.name+'.log'
    self.remoteCommand(cmd, logfilename)
    return

  def startPathLoadServer(self):
    pass
    return

  def startPathLoadClient(self):
    pass
    return

  # log function
  def logcmd(self, cmd):
    self.fileout.write(self.name + ': ' + str(time.time()) +': '+ cmd + '\n')
    print self.name + ': ' + str(time.time()) +': '+ cmd + '\n'
    return

  def allClear(self):
    self.remoteCommand('rm Browserlab/pings/*.log')
    self.remoteCommand('rm testlogs/*.log')
    self.remoteCommand('rm tcpdump/*.pcap')
    return

  # specific functions
  def createDataLogDir(self, description=None):
    """a server function only"""
    if self.name == 'S':
      foldername = str(int(time.mktime(time.localtime())))
      if (description):
        foldername = foldername + '_' + description
      self.remoteCommand('mkdir -p /home/gtnoise/data/'+foldername)
    return foldername

  def remoteLogTransfer(self, srcpath, dstpath):
    """Transfer all logfiles to homenetworklab/data/<DATE>/"""
    # doesn't work. use transferlogs instead
    pass
    # sftp = self.host.open_sftp()
    # sftp.put(srcpath, dstpath)
    # sftp.close()
    return

  def tcpDump(self, logfilename):
    if self.name == 'R':
      cmd = 'tcpdump -s 60 -i any -w tcpdump/'+logfilename
    else:
      cmd = 'echo "gtnoise" | sudo -S -su tcpdump -s 100 -i any -w tcpdump/'+logfilename
    self.host.exec_command(cmd)
    self.logcmd(cmd)
    return

  def getBitRate(self, logfilename):
    # TODO save bitrate value every second
    cmd = '/sbin/iw wlan0 station dump | grep bitrate'
    sin, sout, serr = self.host.exec_command(cmd)
    for line in sout:
      line.split('bitrate:')[2]
    pass
    return



