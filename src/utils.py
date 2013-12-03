import paramiko
import base64
import subprocess
from collections import defaultdict
from constants import *
import time

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
