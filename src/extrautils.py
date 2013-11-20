import subprocess
import paramiko

def remoteIperf(remote, ipaddr, port, logname, **kargs):
  cmd = 'iperf -p '+str(port)+ ' -c '+str(ipaddr)+' -y C -f B'
  savelog = ' >> testlogs/'+logname+' &'
  # window in KM
  if 'w' in kargs:
    cmd += ' -w '+ kargs['w']
  # buffer length in KM
  if 'l' in kargs:
    cmd += ' -l '+ kargs['l']
  # MTU size (in bytes by default)
  if 'M' in kargs:
    cmd += ' -M '+ kargs['M']
  # reverse dual test
  if 'L' in kargs:
    cmd += ' -r -L '+ kargs['L']

  print "command: "+cmd+savelog
  stdin, stdout, stderr = remote.exec_command(cmd+savelog)
  print 'remote iperf-client running'
  return

def localIperf(ipaddr, port, logname, **kargs):
  cmd = ['iperf', '-p', str(port), '-c', str(ipaddr),'-y', 'C', '-f', 'B']
  savelog = ' >> testlogs/'+logname+' &'
  # window in KM
  if 'w' in kargs:
    cmd.append('-w')
    cmd.append(kargs['w'])

  # buffer length in KM
  if 'l' in kargs:
    cmd.append('-l')
    cmd.append(kargs['l'])

  # MTU size (in bytes by default)
  if 'M' in kargs:
    cmd.append('-M')
    cmd.append(kargs['M'])

  # reverse dual test
  if 'L' in kargs:
    cmd.append('-r')
    cmd.append('-L')
    cmd.append(kargs['L'])

  print "command: "
  print cmd#+savelog
  output = subprocess.check_output(cmd)
  return output

