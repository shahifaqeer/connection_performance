from utilfunctions import *
from latencyBWtests import *
from constants import *
import time

def many_run(k, runcounter=0, logname='testrun.log'):
  check_connect(router)
  check_connect(server)

  print "remember to open iperf tcp servers on router (5004), server/B (5005), local (5006)"

  i = 0
  while (i<k):
    ABtest("AB"+str(runcounter)+".log")
    time.sleep(time_sleep)
    BAtest("BA"+str(runcounter)+".log")
    time.sleep(time_sleep)

    ARRBtest("ARRB"+str(runcounter)+".log")
    time.sleep(time_sleep)
    BRRAtest("BRRA"+str(runcounter)+".log")
    time.sleep(time_sleep)

    ABtest("AR"+str(runcounter)+".log")
    time.sleep(time_sleep)
    BAtest("RA"+str(runcounter)+".log")
    time.sleep(time_sleep)

    RBtest("RB"+str(runcounter)+".log")
    time.sleep(time_sleep)
    RBtest("BR"+str(runcounter)+".log")

    i+=1
    time.sleep(3.0)

  return
