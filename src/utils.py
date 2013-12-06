import paramiko
import base64
import subprocess
from collections import defaultdict
from constants import *
import time

# local server ssh parameters to authenticate
# make sure all systems (A, B, S, R) have been ssh-ed into by
# C at least once!
def connectHost(ip, user, passwd):
  host = paramiko.SSHClient()
  host.load_system_host_keys()
  host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  host.connect(ip, username=user, password=passwd)
  return host

def check_connect(host):
  stdin, stdout, stderr = host.exec_command('ls /tmp/')
  for line in stdout:
    print 'check host: ' + line.strip('\n')
  return
