from loggos import loggos as log
import sys

log = log.Loggos(
     public = '',
     secret = '',
     client = 'loadavg',
     client_type = "scheduled",
     fields = '1m, 5m, 15m, nprocs, nsched, pid'
     )

with open("/proc/loadavg", "r") as load:
    ret = load.readlines()[0].replace('\n','').replace('/',' ')
    print(ret)
    log.data(ret)
