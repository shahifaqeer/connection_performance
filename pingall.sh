#!/bin/sh

#A='192.168.10.149'
A='192.168.10.184'
B='192.168.10.158'
C='192.168.10.142'
R='192.168.10.1'
S='192.168.20.1'

echo "usage on machine A: sh pingall.sh 'A' 0.100"
me=$1
int=$2

ping $A -i $int -D >> "Browserlab/pings/$(basename $me)_A.log" &
ping $B -i $int -D >> "Browserlab/pings/$(basename $me)_B.log" &
ping $C -i $int -D >> "Browserlab/pings/$(basename $me)_C.log" &
ping $R -i $int -D >> "Browserlab/pings/$(basename $me)_R.log" &
ping $S -i $int -D >> "Browserlab/pings/$(basename $me)_S.log" &
