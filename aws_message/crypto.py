from django.conf import settings
from django.core.cache import cache
from Crypto.Cipher import AES
from hashlib import sha1
from oscrypto import asymmetric as oscrypto_asymmetric
from oscrypto import errors as oscrypto_errors
import urllib3
import logging

# shunt warnings to logging
logging.captureWarnings(True)


class CryptoException(Exception):
    pass


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

        if cert['type'].lower() == 'url':
            cert_ref = cert['reference']
            key = sha1(cert_ref.encode('utf-8')).hexdigest()
            self._cert = cache.get(key)
            if self._cert is None:
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
                        raise CryptoException(
                            'Cannot get certificate %s: status %s' % (
                                cert_ref, r.status))
                except urllib3.exceptions.HTTPError as err:
                    raise CryptoException(
                        'Cannot get certificate %s: %s' % (cert_ref, err))
        else:
            raise CryptoException('Unrecognized certificate reference type')

    def validate(self, msg, sig):
        if self._cert is None:
            raise CryptoException('Cannot validate: no certificate')

        try:
            oscrypto_asymmetric.rsa_pkcs1v15_verify(
                oscrypto_asymmetric.load_certificate(self._cert),
                sig, msg, 'sha1')
        except oscrypto_errors.SignatureError as err:
            raise CryptoException('Cannot validate: %s' % (err))


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
        except Exception as err:
            raise CryptoException('Cannot decrypt message: %s' % (err))

    def decrypt(self, msg):
        try:
            crypt = AES.new(self._key, AES.MODE_CBC, self._iv)
            return crypt.decrypt(msg)
        except Exception as err:
            raise CryptoException('Cannot decrypt message: %s' % (err))

    def pad(self, s):
        return s + (self._block_size - len(s) % self._block_size) * \
            chr(self._block_size - len(s) % self._block_size)

    def unpad(self, s):
        return s[0:-ord(s[-1])]
