import hmac
import requests
import hashlib
import time
import os, sys
# from urllib import urlencode
from requests.auth import HTTPBasicAuth
import json
from copy import deepcopy
from io import StringIO
from subprocess import Popen, PIPE
import socket

try:
    from Crypto.Hash import HMAC as hmac
    from Crypto.Hash import SHA256 as sha256
except:
    import hmac
    from hashlib import sha256


class Loggos():

    base_url = "https://log.0xf4.de/api/v0.2/"

    def __init__(
            self, public, secret,
            enabled=True, print_to_stdout=False,
            **kwargs):
        self.master_public = public
        self.master_secret = secret
        self.version = 0.11
        self.config = kwargs
        self.enabled = enabled
        self.print = print_to_stdout

        if not self.registered:
            self.register_client(
                    self.master_public,
                    self.master_secret,
                    self.apikey)

    @property
    def apikey(self):
        s = "{}{}{}{}{hostname}{path}".format(
             self.master_public, self.master_secret,
             self.config["client"], self.config["client_type"],
             **self.metadata,)
        return sha256.new(s.encode()).hexdigest()

    @property
    def metadata(self):
        return {
                  "hostname":socket.gethostname(),
                  "path": os.path.abspath(sys.argv[0]),
                  "fields": self.config.get("fields", []),
                  "tags": self.config.get("tags", [])}

    @property
    def secret(self):

        with open(self.client_file, "r") as f:
            return f.readline()

    @property
    def client_file(self):
        return os.path.expanduser("~/.loggos/" + self.apikey)

    @property
    def registered(self):
        f = self.client_file
        return os.path.exists(f)

    @property
    def nonce(self):
        return str(int(time.time() * 1000))

    def register_client(self, master_apikey, master_secret, apikey):
        if not self.enabled:
            return
        print("registering new client {} ".format(apikey))
        msg = {"apikey": self.apikey}
        msg.update(self.metadata)
        private = self.call(
                    method="register", msg=msg,
                    apikey=master_apikey, secret=master_secret)
        print("done")
        with open(self.client_file, "a+") as f:
            f.write(private)

    def call(self, method, msg, apikey=None, secret=None):
        if self.print:
            print(msg)
        if not self.enabled:
            return
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

