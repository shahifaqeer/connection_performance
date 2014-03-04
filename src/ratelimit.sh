interface=$1
down_rate=$2 # "mbps", Megabytes per second
#HZ=$(grep 'CONFIG_HZ=' /boot/config-$(uname -r) | sed 's/CONFIG_HZ=//')
HZ=100 #not sure
down_burst=$(((($down_rate * 1000000) / $HZ)/1000)) # "kb", Kilobytes ; a minimum value should be _at least_ one packet, ~2kb, though it is safer with 10kb
down_limit=$(((($down_rate * 1000000) / $HZ)/1000)) # "kb", Kilobytes ; a minimum value should be _at least_ one packet, ~2kb, though it issafer with 10kb
# first
tc qdisc del dev $interface root
# add as queueing discipline on eth0 at root
# the qdisc is prio (man tc-prio) with two different priority (bands) labeled from 0 to 1 (from 0 to ["bands #" - 1])
# this automaticaly creates 2 class correspondings to the bands and with respective handle :1 and :2 (from handle 1: --> so 1:1 and 1:2)
# the default prioritymap (which depends on the TOS) assigns all traffic by default to the 0 band (which corresponds to handle 1:1 … ).
# ( http://lartc.org/howto/lartc.qdisc.classful.html#AEN924 )
tc qdisc add dev $interface root handle 1: prio bands 2 priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0
# I always find it better to specifiy the filter before adding the queuing discipline to them
# in case I do something wrong to the filter, the qdisc won't be applied and thus the link is preserved
# the filters defined rules such as it takes packets from handle 1: and put them into class 1:2 (which corresponds to band 1 of prio)
# all other will go  in the default band (0 --> class 1:1 )
# ( http://lartc.org/howto/lartc.qdisc.filters.html#AEN1099 )
tc filter add dev $interface parent 1: protocol ip prio 1 u32 match ip dport 22 0xffff flowid 1:2
tc filter add dev $interface parent 1: protocol ip prio 1 u32 match ip sport 22 0xffff flowid 1:2
# then add a tbf to the OTHER class (the one that is not ssh) that is to 1:1 (band 0)
# have in mind that depending on your HZ, burst and limit have to be big enough to allow the specified rate
# see man tc-tbf looks for HZ *****
tc qdisc replace dev $interface parent 1:1 handle 11: tbf rate $down_rate"mbps" burst $down_burst"kb" limit $down_limit"kb"
# it gives you this:
#                                       root
#                                       prio                                 qdisc
#                                        1:                                    handle
#                                     /        \
#                                    0        1                               prio bands
#                                  1:1     1:2                             classes
#                                    |          |
#                                    |          |
#                                  tbf     (null)                           qdisc
#                                  11:                                        handle
#                              not ssh       ssh                           traffic
#
#*****
tc -s qdisc ls dev $interface
