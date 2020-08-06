from time import time
import hashlib
import hmac
from urllib.parse import urlparse

from asks import PreResponseAuth

def authentication_required(fn):
    """Annotation for methods that require auth."""
    def wrapped(self, *args, **kwargs):
        assert self.api_key, "You must be authenticated to use this method"
        return fn(self, *args, **kwargs)
    return wrapped

# Generates an API signature.
# A signature is HMAC_SHA256(secret, verb + path + nonce + data), hex encoded.
# Verb must be uppercased, url is relative, nonce must be an increasing 64-bit integer
# and the data, if present, must be JSON without whitespace between keys.
#
# For example, in psuedocode (and in real code below):
#
# verb=POST
# url=/api/v1/order
# nonce=1416993995705
# data={"symbol":"XBTZ14","quantity":1,"price":395.01}
# signature = HEX(HMAC_SHA256(secret, 'POST/api/v1/order1416993995705{"symbol":"XBTZ14","quantity":1,"price":395.01}'))
def generate_signature(secret, verb, url, nonce, data):
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.
    parsedURL = urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query

    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf8')

    # print "Computing HMAC: %s" % verb + path + str(nonce) + data
    message = verb + path + str(nonce) + data

    signature = hmac.new(bytes(secret, 'utf8'), bytes(message, 'utf8'), digestmod=hashlib.sha256).hexdigest()
    return signature

class APIKeyAuthWithExpires(PreResponseAuth):
    """Generates API Key Authentication headers. This implementation uses `expires`."""

    def __init__(self, api_key, api_secret):
        """Init with Key & Secret."""
        self.api_key = api_key
        self.api_secret = api_secret

    async def __call__(self, r):
        """
        Called when forming a request - generates api key headers. This call uses `expires` instead of nonce.
        This way it will not collide with other processes using the same API Key if requests arrive out of order.
        For more details, see https://www.bitmex.com/app/apiKeys
        """
        # modify and return the request
        expires = int(round(time()) + 5)  # 5s grace period in case of clock skew
        return {
            'api-expires': str(expires),
            'api-key': self.api_key,
            'api-signature': generate_signature(self.api_secret, r.method, r.path, expires, r.body or '')
        }

