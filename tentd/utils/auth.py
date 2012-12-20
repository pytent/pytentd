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

def parse_authstring( authstring ):
    """Parse an auth string into a dict """
    
     #make sure the string starts with 'MAC '
    if not authstring or not authstring.startswith('MAC '):
        return False

    pairs = authstring[4:].strip().split(',')

    vars = {}

    for p in pairs:
        p = p.strip()
        key,value = p.split("=",1)
        vars[key] = value.strip('"')

    return vars

def normalize_request(request):

    auth = parse_authstring(request.headers.get('Authorization'))
    full_path = request.path + "?" + request.query_string
   
    if auth.has_key('ext'):
        ext = auth['ext']
    else:
        ext = ""

    template = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}"
    
    return template.format(auth['ts'], auth['nonce'], 
                                    request.method,
                                    full_path,
                                    request.host,
                                    80,
                                    ext)

def check_request(request,key):
    """ Return true if the given request object matches its signature"""
    
    auth = parse_authstring(request.headers.get('Authorization'))
    
    reqmac = auth['mac']
    norm = normalize_request(request)   
    mac = hmac.new(key, norm, hashlib.sha256)

    macstr = base64.encodestring(mac.digest())

    return reqmac == macstr


def require_authorization(f):
    
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        return f(*args,**kwargs)

    return decorated
