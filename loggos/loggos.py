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

    def __init__(self, public, **kwargs):
        self.master_public = public
        self.master_secret = secret
        self.version = 0.11
        self.config = kwargs

        if not self.registered:
            self.register_client(
                    self.master_public,
                    self.master_secret,
                    self.apikey)

    @property
    def apikey(self):
        m = sha256.sha256()
        return m.update("".join(self.config.items())).hexdigest()


    @property
    def registered:
        f = os.path.expanduser("~/.loggos/" + self.apikey)
        return os.path.exists(f)

    @property
    def nonce(self):
        return str(int(time.time() * 1000))

    def register_client(self, master_apikey, master_secret, apikey):
        self.call("register", apikey=master_apikey, secret=master_secret)

    def call(self, method, msg, apikey=self.apikey, secrect=self.secret):
        req = self.base_url.format(method, apikey, self.nonce, msg)
        h = hmac.new(secret.encode(), digestmod=sha256)
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

