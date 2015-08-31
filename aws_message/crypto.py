#
#  signature and encryption classes
#

from django.conf import settings
from django.core.cache import cache
import string
import urllib3
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    from OpenSSL import crypto
    from Crypto.Cipher import AES
    from hashlib import sha1


class CryptoException(Exception): pass


class Signature(object):
    """
    SHA1 with RSA message signature object
    """

    _cert = None

    def __init__(self, config):
        """
        SHA1 with RSA signed message object

        Takes config object containing certificate reference

        Raises CryptoException
        """
        if config is None:
            raise CryptoException('Missing signature configuration')

        if 'cert' in config:
            cert = config['cert']
        else:
            raise CryptoException('Missing certificate configuration')

        if string.lower(cert['type']) == 'url':
            cert_ref = cert['reference']
            key = sha1(cert_ref).hexdigest()
            self._cert = cache.get(key)
            if self._cert == None:
                try:
                    http = urllib3.PoolManager(
                        cert_reqs='CERT_REQUIRED',
                        ca_certs=settings.AWS_CA_BUNDLE
                    )
                    r = http.request('GET', cert_ref)
                    if r.status == 200:
                        self._cert = r.data
                        cache.set(key, self._cert)
                    else:
                        raise CryptoException('Cannot get certificate: status ' + r.status)
                except urllib3.exceptions.HTTPError, err:
                    raise CryptoException('Cannot get certificate: ' + str(err))
        else:
            raise CryptoException('Unrecognized certificate reference type')

    def validate(self, msg, sig):
        if self._cert == None:
            raise CryptoException('Cannot validate: no certificate')

        try:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, self._cert)
            crypto.verify(cert, sig, msg, 'sha1')
        except Exception, err:
            raise CryptoException('Cannot validate: ' + str(err))


class aes128cbc(object):

    _key = None
    _iv = None
                     
    def __init__(self, key, iv):
        """
        Advanced Encryption Standard object

        Raises CryptoException
        """
        self._block_size = 16

        if key is None:
            raise CryptoException('Missing AES key')
        else:
            self._key = key

        if iv is None:
            raise CryptoException('Missing AES initialization vector')
        else:
            self._iv = iv

    def encrypt(self, msg):
        try:
            crypt = AES.new(self._key, AES.MODE_CBC, self._iv)
            return crypt.encrypt(msg)
        except Exception, err:
            raise CryptoException('Cannot decrypt message: ' + str(err))

    def decrypt(self, msg):
        try:
            crypt = AES.new(self._key, AES.MODE_CBC, self._iv)
            return crypt.decrypt(msg)
        except Exception, err:
            raise CryptoException('Cannot decrypt message: ' + str(err))

    def pad(self, s):
        return s + (self._block_size - len(s) % self._block_size) * chr(self._block_size - len(s) % self._block_size)

    def unpad(self, s):
        return s[0:-ord(s[-1])]
