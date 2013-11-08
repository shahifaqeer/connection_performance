import paramiko
import base64
import subprocess
import time
from collections import defaultdict

#router options
router_pass = 'h0m3n3t' #'bismark123'
router_key_string = 'AAAAB3NzaC1yc2EAAAADAQABAAAAgnH5yk05kTGEaPMDxr61H76uO8TkGKsBZcJBGdip8idCi3Dqaf1Hjr7RDIWCxyr8G8TBeVDSe53kwDqWIz1oa7niVtyTts66/Fbj4NeEEy4wzyNm2M1GgA1+yGsfo9WMtiuPuuAqL+ZFGO9qrcSovk+qpzp2l0THUs+5jf6/6GA5aF0='

#server_options
server_user = 'gtnoise'
server_pass = 'gtnoise'
server_ip = '192.168.142.115'

#bismark router ssh parameters to authenticate
router = paramiko.SSHClient()
#key = paramiko.RSAKey(data=base64.decodestring('AAAAB3NzaC1yc2EAAAADAQABAAAAgwDB/WgmbluGkbThhuciG+J2q02WSJ+wSEPHDgL73n9skmZlMl6aRyTC6j10i0U2C3MJwZBjqq8oP9XcAnDzkpz4rlCd4IVkxgAiOxAKHzjEko4IwkSFVhGZ4pUZN6oDIIasE62xfxFW0NYnanh9dSsj6j4su8UXYU0/QNjpgb98kWgL'))
key = paramiko.RSAKey(data=base64.decodestring(router_key_string))
router.get_host_keys().add('192.168.142.1', 'ssh-rsa', key)
router.connect('192.168.142.1', username='root', password=router_pass)

#local server ssh parameters to authenticate
server = paramiko.SSHClient()
server.load_system_host_keys()
server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
server.connect(server_ip, username=server_user, password=server_pass)

#riverside server ssh parameters to authenticate
#server = paramiko.SSHClient()
#private_key = paramiko.RSAKey.from_private_key_file("/home/gtnoise/.ssh/id_rsa")
#server.load_system_host_keys()
#server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#server.connect('riverside.noise.gatech.edu', username='sarthak', pkey=private_key)

def check_connect(serv):
  stdin, stdout, stderr = serv.exec_command('ls /tmp/')
  for line in stdout:
    print 'serv-check: ' + line.strip('\n')
  return


def remoteIperfServer(serv, port):
  cmd = 'iperf -s -p ' + str(port) + ' &'
  stdin, stdout, stderr = serv.exec_command(cmd)
  print 'iperf-server is running'
  return

def remoteIperfClient(serv, serverAddress, port, logname):
  cmd = 'iperf -p '+str(port)+ ' -c '+str(serverAddress)+' -y C -f B >> testlogs/'+logname+' &'
  stdin, dtdout, stderr = serv.exec_command(cmd)
  print 'remote iperf-client running'
  return

def localIperfClient(serverAddress, port):
  output = subprocess.check_output(['iperf', '-p', str(port), '-c', serverAddress, '-y', 'C', '-f', 'B'])

  return output

def localTraceroute(dst):
  output = subprocess.check_output(['traceroute ', dst ])
  return output

def remoteTraceroute(serverAddress, logname):
  #similar to remote iperf.
  cmd = 'traceroute ' +str(serverAddress)+' >> /tmp/'+logname+' &'
  stdin, dtdout, stderr = serv.exec_command(cmd)
  print 'remote traceroute running'
  return

def localIperfServer(port):
  subprocess.check_output(['iperf', '-s', ' -p', str(port)])
  return

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

def AStest(logname, port_num=5005):
  print "AS test \n"
  time_sleep = 3.0 #seconds
  serverAddress = '192.168.142.115'
  output1 = localIperfClient(serverAddress, port_num)
  print 'local iperf client ' + output1

  time.sleep(time_sleep)

  final_output = output1
  print '... '+ final_output
  f = open('testlogs/'+logname, 'a+w')
  f.write(final_output)
  f.close()
  return

def ARtest(logname, port_num=5004):
  print "AR test \n"
  time_sleep = 3.0 #seconds
  serverAddress = '192.168.142.1'
  output1 = localIperfClient(serverAddress, port_num)
  print 'local iperf client ' + output1

  time.sleep(time_sleep)

  final_output = output1
  print '... '+ final_output
  f = open('testlogs/'+logname, 'a+w')
  f.write(final_output)
  f.close()
  return

def RStest(logname, port_num=5005):
  print "RS test \n"
  time_sleep = 3.0 #seconds
  serverAddress = '192.168.142.115'
  remoteIperfClient(router, serverAddress, port_num, logname)

  time.sleep(time_sleep)

  print "please check testlogs/"+logname+" on the remote client"

  return

def ARRStest(logname, port_num1=5004, port_num2=5005):
  print "AR + RS test \n"
  time_sleep = 3.0 #seconds
  serverAddress = '192.168.142.115'
  routerAddress = '192.168.142.1'

  # RS
  remoteIperfClient(router, serverAddress, port_num2, "R_"+logname)
  print 'iperf client running on router. retrieve log from testlogs/'+logname
  # AR
  output1 = localIperfClient(routerAddress, port_num1)
  print 'local iperf-client: ' + output1

  time.sleep(time_sleep)

  final_output = output1
  print '... '+ final_output
  f = open('testlogs/A_'+logname, 'a+w')
  f.write(final_output)
  f.close()
  return

def SAtest(logname, port_num=5006):
  print "SA test \n"
  time_sleep = 3.0 #seconds
  myAddress = '192.168.142.184'
  remoteIperfClient(server, myAddress, port_num, 'dw_'+logname)
  print "please check testlogs/dw_"+logname+" on the remote client"

  time.sleep(time_sleep)

  return

def RAtest(logname, port_num=5006):
  print "RA test \n"
  time_sleep = 3.0 #seconds
  serverAddress = '192.168.142.184'
  remoteIperfClient(router, myAddress, port_num, 'dw_'+logname)
  print "please check testlogs/dw_"+logname+" on the remote client"

  time.sleep(time_sleep)

  return

def SRtest(logname, port_num=5004):
  print "SR test \n"
  time_sleep = 3.0 #seconds
  serverAddress = '192.168.142.1'
  remoteIperfClient(server, serverAddress, port_num, 'dw_'+logname)

  time.sleep(time_sleep)

  print "please check testlogs/dw_"+logname+" on the remote client"

def SRRAtest(logname, port_num1=5006, port_num2=5004):
  print "AR + RS test \n"
  time_sleep = 3.0 #seconds
  myAddress = '192.168.142.184'
  routerAddress = '192.168.142.1'
  # SR
  remoteIperfClient(server, routerAddress, port_num2, 'dw_S_'+logname)
  print 'iperf client running on server. retrieve log from testlogs/dw_S_'+logname
  # RA
  remoteIperfClient(router, myAddress, port_num1, 'dw_R_'+logname)
  print 'iperf client running on router. retrieve log from testlogs/dw_R_'+logname

  time.sleep(time_sleep)

  return

def many_run(k, runcounter=0, logname='testrun.log'):
  check_connect(router)
  check_connect(server)

  print "open servers on router and server at port 5004 and 5005"

  remoteIperfServer(router, 5004)
  remoteIperfServer(server, 5005)
  localIperfServer(5006)

  i = 0
  while (i<k):
    #AStest("AStest"+str(runcounter)+".log")
    SAtest("SAtest"+str(runcounter)+".log")
    #ARRStest("ARRStest"+str(runcounter)+".log")
    SRRAtest("SRRAtest"+str(runcounter)+".log")
    #ARtest("ARtest"+str(runcounter)+".log")
    RAtest("RAtest"+str(runcounter)+".log")
    #RStest("RStest"+str(runcounter)+".log")
    SRtest("SRtest"+str(runcounter)+".log")

    i+=1
    time.sleep(2.0)

  return
