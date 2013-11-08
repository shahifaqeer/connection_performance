import paramiko, base64
import os
import subprocess
import time
from collections import defaultdict

#logname = input()

#bismark router ssh parameters to authenticate
router = paramiko.SSHClient()
key = paramiko.RSAKey(data=base64.decodestring('AAAAB3NzaC1yc2EAAAADAQABAAAAgwDB/WgmbluGkbThhuciG+J2q02WSJ+wSEPHDgL73n9skmZlMl6aRyTC6j10i0U2C3MJwZBjqq8oP9XcAnDzkpz4rlCd4IVkxgAiOxAKHzjEko4IwkSFVhGZ4pUZN6oDIIasE62xfxFW0NYnanh9dSsj6j4su8UXYU0/QNjpgb98kWgL'))
router.get_host_keys().add('192.168.142.1', 'ssh-rsa', key)
router.connect('192.168.142.1', username='root', password='bismark123')

#riverside server ssh parameters to authenticate
server = paramiko.SSHClient()
private_key = paramiko.RSAKey.from_private_key_file("/home/gtnoise/.ssh/id_rsa")
server.load_system_host_keys()
server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
server.connect('riverside.noise.gatech.edu', username='sarthak', pkey=private_key)


#execute at router
stdin, stdout, stderr = router.exec_command('ls /tmp/')
for line in stdout:
  print 'router-check: ' + line.strip('\n')
#router.close()

#execute at server
stdin, stdout, stderr = server.exec_command('ls Desktop/')
for line in stdout:
  print 'server-check: ' + line.strip('\n')
#server.close()

def startIperfServer(server, port):
  cmd = 'iperf -s -p ' + str(port) + ' &'
  stdin, stdout, stderr = server.exec_command(cmd)
  for line in stdout:
    print 'iperf-server: ' + line.strip('\n')
  return

def stopIperfServer():
  pass
  return

def startIperfClient(serverAddresss, port):
  #cmd = 'bash iperf-client.sh riverside.noise.gatech.edu '+ str(port)
  #subprocess.call([cmd])
  #cmd = 'iperf'
  output = subprocess.check_output(['iperf', '-p', '5002', '-c', 'riverside.noise.gatech.edu', '-y', 'C', '-f', 'B'])
  
  return output

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


#if __name__ == "__main__":

def one_run(logname):
  port_num = 5002
  time_sleep = 1.0 #seconds
  serverAddress = 'riverside.noise.gatech.edu'
  #startIperfServer(server, port_num)	#do this manually instead
  output1 = startIperfClient(serverAddress, port_num)
  print '... ' + output1

  time.sleep(time_sleep)

  stats_transfer = monitorFlow(router, port_num)
  print '... ' + stats_transfer

  final_output = output1.strip('\n') + ',' + stats_transfer + '\n'
  print '... '+ final_output
  f = open('testlogs/'+logname, 'a+w')
  f.write(final_output)
  f.close()
  return

def many_run(k, logname):
  i = 0
  while (i<k):
    one_run(logname)
    i+=1
    time.sleep(2.0)
