import tests

from unittest import TestCase

from tentd.utils.auth import generate_keypair

class AuthTest(TestCase):

    def test_hmac(self):
        print generate_keypair()
        pass        
