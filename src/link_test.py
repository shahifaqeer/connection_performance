from __future__ import division
import time
import paramiko
import subprocess
#from link_constants import *

# TODO what kinda commands should I be sending?
# just iperf_tcp_up doesn't seem to be enough as client
# can test to both server and router :(
# also may be a good idea to separate client ip, server ip,
# and router ip functions so that I can get them at host
# and simply use them elsewhere

# TODO iperf_tcp_up may
def initialize_logfile():
  if not os.path.exists('/tmp/browserlab/'):
    os.mkdir('/tmp/browserlab/')
  FILEOUT = open('/tmp/browserlab/logcmd.log', 'a+w')
  return FILEOUT

def logcmd(cmd, name, LOGFILE):
  LOGFILE.write(name + ': ' + str(time.time()) +': '+ cmd + '\n')
  print 'LOGFILE: '+ name + ': ' + str(time.time()) +': '+ cmd
  return


class Router:
  def __init__(self, ip, user, passwd):
    self.ip = ip
    self.user = user
    self.passwd = passwd
    self.name = 'R'
    self.logfile = initialize_logfile()

    self.server = '130.207.97.240'
    self.client = '192.168.1.153'
    self.router = '192.168.1.1'

    self.host = self.connectHost(ip, user, passwd)

    self.host.remoteCommand('mkdir -p /tmp/browserlab/')
    self.busy = 0
    self.command_to_cmd = self.initialize_command_mapping()
    self.initialize_servers()

  def connectHost(self, ip, user, passwd):
    host = paramiko.SSHClient()
    host.load_system_host_keys()
    host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print 'DEBUG: connect to ' + ip + ' user: ' + user + ' pass: ' + passwd
    host.connect(ip, username=user, password=passwd)
    return host

  def remoteCommand(self, cmd, logfilename=None, background=0):
    """This should be used for starting iperf servers, pings,
    tcpdumps, etc.

    Commands issued here can be killed by cmd = 'killall or pkill'"""
    if logfilename:
      cmd = cmd + ' >> /tmp/browserlab/' + logfilename
    if (background):
      cmd = cmd + ' &'

    stdin, stdout, stderr = self.host.exec_command(cmd)
    for line in stdout:
      print 'DEBUG: '+ line

    logcmd(cmd, self.name, self.logfile)
    return

  def command(self, command):
    """Map cmd sent by main function to sensible cmd to exec
    on router"""
    cmd, logfilename, background = self.command_to_cmd_map[command]
    if cmd == 0:
      self.busy = 1
      print "DEBUG: error getting proper command from cmd sent by host"
    else:
      self.busy = 0
      self.remoteCommand(cmd, logfilename, background)
    return self.busy

  def initialize_command_mapping(self):
    MAP = defaultdict(int)
    MAP['iperf_tcp_up'] = ('iperf -c ' + self.server, self.name+'_iperf_tcp_up.log', 1)
    MAP['iperf_tcp_dw'] = ('iperf -c ' + self.client, self.name+'_iperf_tcp_dw.log', 1)
    MAP['iperf_udp_up'] = ('iperf -c ' + self.server+ ' -u -b 150M', self.name+'_iperf_udp_up.log', 1)
    MAP['iperf_udp_dw'] = ('iperf -c ' + self.client+ ' -u -b 150M', self.name+'_iperf_udp_dw.log', 1)
    MAP['fping']        = ('fping ' + self.client + ' ' + self.server + ' -p -l -r 1 -A', self.name+'_fping.log', 1)
    MAP['udp_probe_up'] = 0
    MAP['udp_probe_dw'] = 0
    # TODO tcpdump
    return MAP

  def initialize_servers(self):
    # iperf tcp serverip
    self.remoteCommand('iperf -s', self.name + '_iperf_tcp_server.log', 1)
    # iperf udp server
    self.remoteCommand('iperf -s -u', self.name + '_iperf_udp_server.log', 1)
    # udp probe server
    self.remoteCommand('udpprobeserver', self.name + '_udpprobe_server.log', 1)


class Host:
  def __init__():
    self.name = 'A'
    self.ip = findMyIP()
    self.gwip = findGWIP()

    self.logfile = initialize_logfile()

    self.server = '130.207.97.240'
    self.client = '192.168.1.153'
    self.router = '192.168.1.1'

    self.busy = 0
    self.command_to_cmd = self.initialize_command_mapping()
    self.initialize_servers()

  def findMyIP(self):
    # TODO by parsing ifconfig
    return '192.168.1.153'

  def findGWIP(self):
    # TODO by parsing route -n | grep 'gw'
    return '192.168.1.1'

  def command(self, cmd):
    """Map cmd sent by main function to sensible cmd to exec
    on router"""
    cmd, logfilename, background = self.command_to_cmd_map[cmd]
    if cmd == 0:
      self.busy = 1
      print "DEBUG: error getting proper command from cmd sent by host"
    else:
      self.busy = 0
      self.remoteCommand(cmd, logfilename, background)
    return self.busy

  def remoteCommand(self, cmd):
    """This should be used for starting iperf servers, pings,
    tcpdumps, etc.

    Commands issued here can be killed by cmd = 'killall or pkill'"""
    if logfilename:
      out = open("/tmp/browserlab/"+logfilename,"w")
    if (background):
      cmd = cmd + ' &'
    #if sudo and self.name != 'R':
    #  cmd = 'echo "gtnoise" | sudo -S '+cmd
    DETACHED_PROCESS = 0x00000008
    subprocess.call(cmd, shell=True, stdout=out, creationflags=DETACHED_PROCESS)

    logcmd(cmd, self.name, self.logfile)
    return

  def initialize_command_mapping(self):
    MAP = defaultdict(int)
    MAP['iperf_tcp_up'] = ('iperf -c ' + self.server, self.name+'_iperf_tcp_up.log', 1)
    MAP['iperf_tcp_dw'] = # TODO iperf with -r flag here if against server
    #('iperf -c ' + self.client, self.name+'_iperf_tcp_dw.log', 1)
    MAP['iperf_udp_up'] = ('iperf -c ' + self.server+ ' -u -b 150M', self.name+'_iperf_udp_up.log', 1)
    MAP['iperf_udp_dw'] = # TODO iperf with -r flag here
    #('iperf -c ' + self.client+ ' -u -b 150M', self.name+'_iperf_udp_dw.log', 1)
    MAP['fping']        = ('fping ' + self.router + ' ' + self.server + ' -p c 100 -r 1 -A', self.name+'_fping.log', 1)
    MAP['udp_probe_up'] = 0
    MAP['udp_probe_dw'] = 0
    # TODO tcpdump
    return MAP

  def initialize_servers(self):
    # iperf tcp serverip
    self.remoteCommand('iperf -s', self.name + '_iperf_tcp_server.log', 1)
    # iperf udp server
    self.remoteCommand('iperf -s -u', self.name + '_iperf_udp_server.log', 1)
    # udp probe server
    self.remoteCommand('udpprobeserver', self.name + '_udpprobe_server.log', 1)


class Server:
  def __init__:
    self.ip = '130.207.97.240'
    self.router = self.get_extern_ip_from_connection()

  def command(self, cmd):
    return cmd

  def get_extern_ip_from_connection(self):
    return '50.167.212.31'

  # TODO iperf dw commands using -r flag
  # TODO fping
  # TODO tcpdump

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
      remotehost.remoteCommand('fping '+list_of_ip+' -p '+str(interval)+' -l -r 1 -c 100 -A -b '+str(size_bytes), 'fping.log', 1 , 1)
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
