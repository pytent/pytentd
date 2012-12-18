""" 
Set of functions for enforcing hmac authentication

"""
import hashlib
import hmac
import string
import uuid
import base64

from random import randint, getrandbits
from flask import request

def generate_keypair():
    """Generate an id and 256-bit key for HMAC signing"""
    #generate the key - a uuid
    key = hashlib.sha224(str(getrandbits(512))).hexdigest()
    id  = hashlib.md5( str(getrandbits(256))).hexdigest()
    return id,key

def require_authorization(f):
    
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        print auth
        return f(*args,**kwargs)

    return decorated
