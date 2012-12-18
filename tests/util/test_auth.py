import tests

from flask import request

from unittest import TestCase

from tentd.utils.auth import generate_keypair, check_request, parse_authstring

class AuthTest(tests.AppTestCase):
    
    def before(self):
        self.macid  = "s:f5949a1d"
        self.tstamp = 1355181298
        self.nonce  = "b07235"
        self.mac    = "swgy4RpdIBaFpA1hmAbZrph24VVg9FwmJgMm9GkgiLE="


        template = """MAC id="{0}",ts="{1}",nonce="{2}",mac="{3}" """

        self.authstring = template.format( self.macid, 
                                self.tstamp, 
                                self.nonce, 
                                self.mac)


    def test_parseauth(self):
      
      auth = parse_authstring( self.authstring)
      assert auth['id'] == self.macid
      assert int(auth['ts']) == self.tstamp
      assert auth['nonce'] == self.nonce
      assert auth['mac'] == self.mac

    def test_check_request(self):
        
        headers = [ ("Authorization", self.authstring)]

        with self.client as c:
            c.get(path="/", headers=headers)
            assert check_request(request) == True
        

    def test_hmac(self):
        generate_keypair()
        pass        
