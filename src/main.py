from utilfunctions import *
from bandwidthtests import *
from latencytests import *
from extrautils import *
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


def bandwidthAndLatency(k, runcounter=0, pingcount=30, logname='testrun.log'):

  router = connectRouter()
  B_host = connectHost(B_ip, B_user, B_pass)

  check_connect(router)
  check_connect(B_host)

  print "remember to open iperf tcp servers on B (5005), client (5006), and router (5004)"
  print "also try udp stuff sometime..."

  i = 0
  while (i<k):
    print "RUN "+str(i)

    print str(time.time()) + "AB and BA iperf/ping"
    logcmd("AB and BA iperf/ping")
    ABiperf("AB"+str(runcounter)+".log", B_ip, B_port)
    BAiperf("BA"+str(runcounter)+".log", A_ip, A_port, B_host)
    time.sleep(time_sleep)

    ABping("AB"+str(runcounter)+".log", B_ip, pingcount)
    BAping(B_host, "BA"+str(runcounter)+".log", B_ip, pingcount)
    time.sleep(time_sleep)

    print str(time.time()) + "ARB and BRA iperf/ping"
    logcmd("ARB and BRA iperf/ping")
    ARRBiperf("ARRB"+str(runcounter)+".log", B_ip, B_port, R_ip, R_port, router)
    BRRAiperf("BRRA"+str(runcounter)+".log", R_ip, R_port, A_ip, A_port, B_host, router)
    time.sleep(time_sleep)

    ARRBping("ARRB"+str(runcounter)+".log", B_ip, pingcount, R_ip, pingcount, router)
    BRRAping("BRRA"+str(runcounter)+".log", R_ip, pingcount, A_ip, pingcount, B_host, router)
    time.sleep(time_sleep)

    print str(time.time()) + "AR and RA iperf/ping"
    logcmd("AR and RA iperf/ping")
    ABiperf("AR"+str(runcounter)+".log", R_ip, R_port)
    BAiperf("RA"+str(runcounter)+".log", A_ip, A_port, router)
    time.sleep(time_sleep)

    ABping("AR"+str(runcounter)+".log", R_ip, pingcount)
    BAping(router, "RA"+str(runcounter)+".log", A_ip, pingcount)
    time.sleep(time_sleep)

    print str(time.time()) + "RB and BR iperf/ping"
    logcmd("RB and BR iperf/ping")
    RBiperf("RB"+str(runcounter)+".log", B_ip, B_port, router)
    time.sleep(time_sleep)
    RBiperf("BR"+str(runcounter)+".log", R_ip, R_port, B_host)
    time.sleep(time_sleep)

    BAping(router, "RB"+str(runcounter)+".log", B_ip, pingcount)
    time.sleep(time_sleep)
    BAping(B_host, "BR"+str(runcounter)+".log", R_ip, pingcount)
    time.sleep(time_sleep)

    i+=1
    time.sleep(3.0)

  return

def bandwidthParameters(k, runcounter=0, logname='bandwidthparams.log'):

  router = connectRouter()

  check_connect(router)

  print "remember to open iperf tcp servers on B (5005), client (5006)"

  M_list = ['10', '40', '100'] # 40 is default, 100 gives 536 which seems to be max
  w_list = ['4K', '20K', '40K', '80K', '120K', '160K'] #646K or 8K by default, value given gets doubled, 320 seems max
  l_list = ['10K', '100K', '1M', '10M'] # no idea about this buffer length option. best should be in 1 M area

  i = 0
  while (i<k):
    print "Bandwidth test run "+str(i)+"\n"

    for M in M_list:
      for w in w_list:
        for l in l_list:
          print 'A --> B and back again with_M_'+M+'_w_'+w+'_l_'+l
          logname = 'bw_M_'+M+'_w_'+w+'_l_'+l+'.log'
          output = localIperf(B_ip, B_port, logname, w=w, M=M, l=l, L='5006')
          saveOutput('testlogs/'+logname, output1)
