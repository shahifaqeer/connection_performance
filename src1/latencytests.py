from utilfunctions import *
from constants import *


def ABping(logname, ipaddr, cnt):
  """local A to remote B (server or router)"""
  print "AB test \n"

  output1 = localPing(ipaddr, cnt)
  print 'local ping client ' + output1
  saveOutput('ping_'+logname, output1)
  return

def BAping(remote, logname, ipaddr, cnt):
  """Remote B (server or router) to local A server"""
  print "BA test \n"
  remotePing(remote, ipaddr, "ping_"+logname, cnt)

  print "please check testlogs/ping_"+logname+" on the remote client"
  return


def ARRBping(logname, ipaddr1, cnt1, ipaddr2, cnt2, remote):
  #ipaddr1 is server/B as listener
  #remote is router
  #ipaddr2 is router/R as listener

  print "AR + RB test \n"

  # RS ipaddr1, port_num1 are IPaddress and iperf port on server, remote is router
  BAping(remote, "R_"+logname, ipaddr1, cnt1)
  # AR ipaddr2, port_num2 are IPaddress and iperf port on router
  ABping("A_"+logname, ipaddr2, cnt2)

  return

def BRRAping(logname, ipaddr2, cnt2, ipaddr3, cnt3, remote1, remote2):
  #ipaddr2, cnt2: R as listener; remote1: B as sender
  #ipaddr3, cnt3: A as listener; remote2: R as sender
  print "AR + RS test \n"

  # SR ipaddr1, port_num1 are IPaddress and iperf port on server, remote is router
  BAping(remote1, "B_"+logname, ipaddr2, cnt2)
  # RA
  BAping(remote2, "R_"+logname, ipaddr3, cnt3)

  return
