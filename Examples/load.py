from loggos import loggos as log
import sys

log = log.Loggos(
     public = '',
     secret = ''
     )

with open("/proc/loadavg", "r") as load:
    ret = load.readlines()[0].replace('\n','').replace('/',' ')
    print(ret)
    log.data(ret)
