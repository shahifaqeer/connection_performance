import paramiko, base64

router = paramiko.SSHClient()

key = paramiko.RSAKey(data=base64.decodestring('AAAAB3NzaC1yc2EAAAADAQABAAAAgwDB/WgmbluGkbThhuciG+J2q02WSJ+wSEPHDgL73n9skmZlMl6aRyTC6j10i0U2C3MJwZBjqq8oP9XcAnDzkpz4rlCd4IVkxgAiOxAKHzjEko4IwkSFVhGZ4pUZN6oDIIasE62xfxFW0NYnanh9dSsj6j4su8UXYU0/QNjpgb98kWgL'))
router.get_host_keys().add('192.168.142.1', 'ssh-rsa', key)
router.connect('192.168.142.1', username='root', password='bismark123')

server = paramiko.SSHClient()
private_key = paramiko.RSAKey.from_private_key_file("/home/gtnoise/.ssh/id_rsa")
server.load_system_host_keys()
server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
server.connect('riverside.noise.gatech.edu', username='sarthak', pkey=private_key)



stdin, stdout, stderr = router.exec_command('ls /tmp/')
for line in stdout:
  print '... ' + line.strip('\n')
router.close()

stdin, stdout, stderr = server.exec_command('ls Desktop/')
for line in stdout:
  print '... ' + line.strip('\n')
server.close()

