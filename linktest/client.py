#CLIENT
from __future__ import division
from datetime import datetime
from commands import *

import time
import socket
import schedule
import os
from random import randint


def initialize_devices():
    devs = Devices()
    return devs

def experiment2(devs):
    no_traffic(R)
    iperf_tcp_up(R)
    iperf_tcp_dw(R)


if __name__ == "__main__":

    #schedule.every(1).minutes.do(experiment)

    if True:
        experiment2()
    #   schedule.run_pending()

