import base64
import hmac
from hashlib import sha256

from flask import request

from tentd.utils.auth import *
from tentd.tests import TentdTestCase

class AuthTest(TentdTestCase):
    macid  = "s:f5949a1d"
    tstamp = 1355181298
    nonce  = "b07235"
    mac    = "swgy4RpdIBaFpA1hmAbZrph24VVg9FwmJgMm9GkgiLE="

    def before(self):
        """Set up mock request before each test """
        self.generate_authstring()

    def generate_authstring(self):
        self.authstring = 'MAC id="{0}",ts="{1}",nonce="{2}",mac="{3}"'.format(
            self.macid, self.tstamp, self.nonce, self.mac)

    def test_parseauth(self):
      """Test the parse authstring method """

      auth = parse_authstring(self.authstring)
      assert auth['id'] == self.macid
      assert int(auth['ts']) == self.tstamp
      assert auth['nonce'] == self.nonce
      assert auth['mac'] == self.mac

    def test_check_request(self):
        key = "secret"

        # Build a normalized request string
        norm = "\n".join([
            str(self.tstamp), self.nonce, "GET", "/?apple=2",
            self.app.config['SERVER_NAME'], str(80), ""])
        
        self.mac = base64.encodestring(hmac.new(key, norm, sha256).digest())
        self.generate_authstring()

        headers = [("Authorization", self.authstring)]

        with self.client as c:
            c.get(path="/?apple=2", headers=headers)
            assert check_request(request, key) == True

    def test_hmac(self):
        generate_keypair()
