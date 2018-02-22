import hmac
import requests
import hashlib
import time
import os
# from urllib import urlencode
from requests.auth import HTTPBasicAuth
import json
from copy import deepcopy
from io import StringIO
from subprocess import Popen, PIPE

try:
    from Crypto.Hash import HMAC as hmac
    from Crypto.Hash import SHA256 as sha256
except:
    import hmac
    from hashlib import sha256


class Loggos():

    base_url = "https://log.0xf4.de/api/v0.2/"

    def __init__(self, public, secret, **kwargs):
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
        config = deepcopy(self.config)
        config["fields"] = ",".join(config["fields"])
        s = "".join(config.values())
        return sha256.new(s.encode()).hexdigest()

    @property
    def secret(self):

        with open(self.client_file, "r") as f:
            return f.readline()

    @property
    def client_file(self):
        return os.path.expanduser("~/.loggos/" + self.apikey)

    @property
    def registered(self):
        f = os.path.expanduser("~/.loggos/" + self.apikey)
        return os.path.exists(f)

    @property
    def nonce(self):
        return str(int(time.time() * 1000))

    def register_client(self, master_apikey, master_secret, apikey):
        private = self.call(
                    method="register", msg={
                        "apikey":self.apikey,
                        "path": "/foo/bar",
                        "fields": self.config.get("fields", []),
                        "tags": self.config.get("tags", [])},
                    apikey=master_apikey, secret=master_secret)
        with open(self.client_file, "a+") as f:
            f.write(private)

    def call(self, method, msg, apikey=None, secret=None):
        if not apikey:
            apikey = self.apikey
        if not secret:
            secret = self.secret

        h = hmac.new(secret.encode(), digestmod=sha256)
        h.update((apikey+self.nonce+json.dumps(msg)).encode())

        ret = requests.post(
            self.base_url,
            json={
                "apisign": h.hexdigest(),
                "apikey":  apikey,
                "nonce":   self.nonce,
                "method":  method,
                "message": msg,
                },
            )
        return ret.json()["resp"]


    def info(self, msg):
        self.call("info", msg)

    def error(self, msg):
        self.call("error", msg)

    def warn(self, msg):
        self.call("warn", msg)

    def data(self, msg):
        self.call("data", msg)

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

