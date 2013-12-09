from utils import RemoteHost
from constants import *

# connect ALL hosts
A = RemoteHost(A_ip, A_user, A_pass, A_port, A_udp)
B = RemoteHost(B_ip, B_user, B_pass, B_port, B_udp)
C = RemoteHost(C_ip, C_user, C_pass, C_port, C_udp)
R = RemoteHost(R_ip, R_user, R_pass, R_port, R_udp)
S = RemoteHost(S_ip, S_user, S_pass, S_port, S_udp)

# start ALL iperf servers (already done for now locally)
# start ALL pings
A.startPingAll()
B.startPingAll()
C.startPingAll()
R.startPingAll()
S.startPingAll()

#testsuite iperf -r
