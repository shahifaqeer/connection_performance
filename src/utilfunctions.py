import paramiko
import base64
import subprocess
from collections import defaultdict
from constants import *
import time

#bismark router ssh parameters to authenticate
def connectRouter():
  router = paramiko.SSHClient()
  key = paramiko.RSAKey(data=base64.decodestring(R_key_string))
  router.get_host_keys().add(R_ip, 'ssh-rsa', key)
  router.connect(R_ip, username='root', password=R_pass)
  return router

#local server ssh parameters to authenticate
def connectHost(ip, user, passwd):
  host = paramiko.SSHClient()
  host.load_system_host_keys()
  host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  host.connect(ip, username=user, password=passwd)
  return host

def check_connect(serv):
  stdin, stdout, stderr = serv.exec_command('ls /tmp/')
  for line in stdout:
    print 'check: ' + line.strip('\n')
  return

#don't use this. instead open remote server yourself.
def remoteIperfServer(serv, port):
  cmd = 'iperf -s -p ' + str(port) + ' &'
  stdin, stdout, stderr = serv.exec_command(cmd)
  print 'iperf-server is running'
  return

#might need to use this for sync issues
def remoteIperfClient(serv, serverAddress, port, logname):
  cmd = 'iperf -p '+str(port)+ ' -c '+str(serverAddress)+' -y C -f B >> testlogs/'+logname+' &'
  stdin, stdout, stderr = serv.exec_command(cmd)
  print 'remote iperf-client running'
  return

#use this for output
def localIperfClient(serverAddress, port):
  output = subprocess.check_output(['iperf', '-p', str(port), '-c', serverAddress, '-y', 'C', '-f', 'B'])
  return output

#no need to use this
def localIperfServer(port):
  subprocess.check_output(['iperf', '-s', '-p', str(port)])
  return

#use this for output
def localTraceroute(dst):
  output = subprocess.check_output(['traceroute ', dst ])
  return output

#use this for output
def localPing(dst, cnt=30):
  output = subprocess.check_output(['ping', dst, '-c', cnt ])
  return output

#similar to remote iperf.
def remoteTraceroute(serverAddress, logname):
  cmd = 'traceroute ' +str(serverAddress)+' >> testlogs/'+logname+' &'
  stdin, stdout, stderr = serv.exec_command(cmd)
  print 'remote traceroute running'
  return

#similar to remote iperf.
def remotePing(serverAddress, logname, cnt=30):
  cmd = 'ping ' +str(serverAddress)+' -c' + str(cnt) + ' >> testlogs/'+logname+' &'
  stdin, stdout, stderr = serv.exec_command(cmd)
  print 'remote ping running'

def saveOutput(logname):
  final_output = output1
  f = open('testlogs/'+logname, 'a+w')
  f.write(final_output)
  f.close()
  return

def logcmd(something):
  f = open('logcmd.log', 'a+w')
  f.write(str(time.time()) +': '+ something)
  f.close()
  return

#don't need this for now
def monitorFlow(router, port):
  cmd = 'cat /proc/net/nf_conntrack | grep sport=' + str(port)
  stdin, stdout, stderr = router.exec_command(cmd)
  #parse stdout to get max time's packet counters

  conntrack_vals = defaultdict(int)
  conntrack_consts = []
  max_time_out = 0

  for line in stdout:
    print '... ' + line.strip('\n')
    for x in line.split(' '):
      y=x.split('=')
      if len(y)==1 and y[0] != '':
	conntrack_consts.extend(y)
      elif len(y)>1:
	if conntrack_vals.has_key(y[0]):
	  conntrack_vals[y[0]+str(2)] = y[1]
	else:
	  conntrack_vals[y[0]] = y[1]
    if int(conntrack_consts[4]) >= 115:
      print 'consts: '
      print conntrack_consts
      break

  bytes_n_packets = str(conntrack_vals['bytes']) + ',' + str(conntrack_vals['packets'])
  return bytes_n_packets
