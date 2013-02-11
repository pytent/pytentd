"""Test the authentication functions"""

import base64
import hmac
from hashlib import sha256

from flask import request, current_app

from tentd.utils.auth import parse_authstring, check_request
from tentd.tests.http import GET

class TestAuth(object):
    mac_id = "s:f5949a1d"
    mac_ts = 1355181298
    mac_nonce = "b07235"
    mac = "swgy4RpdIBaFpA1hmAbZrph24VVg9FwmJgMm9GkgiLE="

    def authstring(self):
        return 'MAC id="{id}",ts="{ts}",nonce="{nonce}",mac="{mac}"'.format(
            id=self.mac_id, ts=self.mac_ts,
            nonce=self.mac_nonce, mac=self.mac)
    
    def test_parse_authstring(self):
        """Test the parse_authstring() method """
        auth = parse_authstring(self.authstring())
        assert str(auth['id']) == self.mac_id
        assert int(auth['ts']) == self.mac_ts
        assert str(auth['nonce']) == self.mac_nonce
        assert str(auth['mac']) == self.mac

    def test_check_request(self, app):
        key = "secret"

        # Build a normalized request string
        norm = "\n".join([
            str(self.mac_ts), self.mac_nonce, "GET", "/?apple=2",
            app.config['SERVER_NAME'], str(80), ""])
        
        self.mac = base64.encodestring(hmac.new(key, norm, sha256).digest())

        headers = [("Authorization", self.authstring())]

        with app.test_request_context("/?apple=2", headers=headers) as rc:
            assert check_request(rc.request, key) == True
