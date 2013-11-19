from utilfunctions import *
from constants import *


def ABping(logname, ipaddr, port_num):
  """local A to remote B (server or router)"""
  print "AB test \n"

  output1 = localIperfClient(ipaddr, port_num)
  print 'local ping client ' + output1
  saveOutput('ping_'+logname)
  return

def BAping(logname, ipaddr, port_num, remote):
  """Remote B (server or router) to local A server"""
  print "BA test \n"
  remoteIperfClient(remote, ipaddr, port_num, "ping_"+logname)

  print "please check testlogs/ping_"+logname+" on the remote client"
  return

def RBping(logname, ipaddr, port_num, remote):
  """Remote client and remote listener
  ipaddr, port_num: listener IP:PORT
  remote: client"""
  print "RB/BR test \n"
  remoteIperfClient(remote, ipaddr, port_num, "ping_"+logname)

  print "please check testlogs/ping_"+logname+" on the remote client"
  return

def ARRBping(logname, ipaddr1, port_num1, ipaddr2, port_num2, remote):
  """ipaddr1, port_num1 are server/B as listener
  remote is router
  ipaddr2, port_num2 are router as listener"""

  print "AR + RB test \n"

  # RS ipaddr1, port_num1 are IPaddress and iperf port on server, remote is router
  RBtest("R_"+logname, ipaddr1, port_num1, remote)
  # AR ipaddr2, port_num2 are IPaddress and iperf port on router
  ABtest("A_"+logname, ipaddr2, port_num2)

  return

def BRRAping(logname, ipaddr2, port_num2, ipaddr3, port_num3, remote1, remote2):
  """ipaddr2, port_num2: R as listener; remote1: B as sender
  ipaddr3, port_num3: A as listener; remote2: R as sender"""
  print "AR + RS test \n"

  # SR
  RBtest("B_"+logname, ipaddr2, port_num2, remote1)
  # RA
  RBtest("R_"+logname, ipaddr3, port_num3, remote2)

  return
