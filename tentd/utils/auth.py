""" 
Set of functions for enforcing hmac authentication

A set of utilities that implement HMAC authorization as described in the IETF
specification and as required by the tent protocol.

"""
import hmac
import base64
import flask

from hashlib import sha256, md5
from random import getrandbits

def generate_keypair():
    """Generate an id and 256-bit key for HMAC signing"""
    #generate the key - a uuid
    key = sha256(str(getrandbits(512))).hexdigest()
    keyid  = md5( str(getrandbits(256))).hexdigest()
    return keyid, key

def parse_authstring( authstring ):
    """Parse an auth string into a dict 
    
    Given an authentication header string [RFC2617], parse the fields and
    return a dict object of each key/pair
    """
    
     #make sure the string starts with 'MAC '
    if not authstring or not authstring.startswith('MAC '):
        return False

    pairs = authstring[4:].strip().split(',')

    avars = {}

    for pair in pairs:
        pair = pair.strip()
        key, value = pair.split("=", 1)
        avars[key] = value.strip('"')

    return avars

def normalize_request(request):
    """Build a normalized request string from a request
    
    Take the flask request object and build a normalized request string 
    as defined in the IETF MAC proposal document 

    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01
    """

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

def check_request(request, key):
    """Return true if the given request object matches its signature
    
    This is the main test method that verifies that request
    """
    
    auth = parse_authstring(request.headers.get('Authorization'))
    
    reqmac = auth['mac']
    norm = normalize_request(request)   
    mac = hmac.new(key, norm, sha256)

    macstr = base64.encodestring(mac.digest())

    return reqmac == macstr


def require_authorization(func):
    """Annotation that forces the view to do HMAC auth
    
    Apply this decorator to your view to ensure that the browser is
    authenticated. If they are not, they'll get a HTTP 401 and a
    WWW-Authenticate header.
    
    """

    def decorated(*args, **kwargs):
        """Wrapped decorator function"""
        
        #TODO: actual implementation of this decorator.
        auth = flask.request.headers.get('Authorization')
        return func(*args, **kwargs)

    return decorated
