import hmac
import requests
import hashlib
import time
# from urllib import urlencode

from subprocess import Popen, PIPE

try:
    from Crypto.Hash import HMAC as hmac
    from Crypto.Hash import SHA256 as sha256
except:
    import hmac
    from hashlib import sha256


class Loggos():

    base_url = "http://log.0xf4.de/api/v0.1/{}/{}/{}/{}"

    def __init__(self, public, secret):
        self.public = public
        self.secret = secret

    @property
    def nonce(self):
        return str(int(time.time() * 1000))

    def call(self, method, msg):
        req = self.base_url.format(method, self.public, self.nonce, msg)
        h = hmac.new(self.secret.encode(), digestmod=sha256)
        h.update(req.encode())

        print(requests.get(
            req,
            headers={"apisign": h.hexdigest()}
            ))#.json()

    def info(self, msg):
        self.call("info", msg)

    def error(self, msg):
        self.call("error", msg)

    def warn(self, msg):
        self.call("warn", msg)

    def data(self, msg):
        self.call("data_Raw", msg)

    def capture(self, process, args, info=True):
        try:
            self.info("started {}".format(process)) 
            # ret = subprocess.run(arg, check=True)
            with Popen(args, stdout=PIPE) as proc:
                 # self.info(proc.stdout.read())
                 print(proc.stdout.read())
                 proc.wait()
            self.info("finished {}".format(process))
        except Exception as e:
            self.error(e)

