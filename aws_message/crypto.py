# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from commonconf import settings
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.exceptions import UnsupportedAlgorithm, InvalidSignature
from memcached_clients import PymemcacheClient
from hashlib import sha1
import urllib3
import logging

# shunt warnings to logging
logging.captureWarnings(True)


class CryptoException(Exception):
    pass


class Signature(object):
    """
    SHA1 with RSA message signature object

    For reference:
    https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#verification
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
            cache = PymemcacheClient()
            cert_ref = cert['reference']
            key = sha1(cert_ref.encode('utf-8')).hexdigest()
            self._cert = cache.get(key)
            if self._cert is None:
                try:
                    http = urllib3.PoolManager(
                        cert_file=config.get('cert_file'),
                        key_file=config.get('key_file'),
                        cert_reqs='CERT_REQUIRED',
                        ca_certs=settings.AWS_CA_BUNDLE
                    )
                    r = http.request('GET', cert_ref)
                    if r.status == 200:
                        self._cert = r.data
                        cache.set(key, self._cert, expire=60*60*24*7)
                    else:
                        raise CryptoException(
                            'Cannot get certificate {}: status {}'.format(
                                cert_ref or 'None', r.status))
                except urllib3.exceptions.HTTPError as err:
                    raise CryptoException(
                        'Cannot get certificate {}: {}'.format(
                            cert_ref or 'None', err))
        else:
            raise CryptoException('Unrecognized certificate reference type')

    def validate(self, msg, sig):
        if self._cert is None:
            raise CryptoException('Cannot validate: no certificate')

        try:
            cert = load_pem_x509_certificate(self._cert)
            public_key = cert.public_key()
            public_key.verify(sig, msg, PKCS1v15(), SHA1())

        except (ValueError, UnsupportedAlgorithm, InvalidSignature) as err:
            raise CryptoException('Cannot validate: {}'.format(err))


class aes128cbc(object):
    """
    Advanced Encryption Standard object

    For reference:
    https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
    """

    _key = None
    _iv = None

    def __init__(self, key, iv):
        if key is None:
            raise CryptoException('Missing AES key')
        if iv is None:
            raise CryptoException('Missing AES initialization vector')

        self._key = self.str_to_bytes(key)
        self._iv = self.str_to_bytes(iv)

    def decrypt(self, msg):
        msg = self.str_to_bytes(msg)
        try:
            cipher = Cipher(algorithms.AES(self._key), modes.CBC(self._iv))
            decryptor = cipher.decryptor()
            dct = decryptor.update(msg) + decryptor.finalize()
            return dct
        except Exception as err:
            raise CryptoException(f'Cannot decrypt message: {err}')

    def str_to_bytes(self, s):
        u_type = type(b''.decode('utf8'))
        if isinstance(s, u_type):
            return s.encode('utf8')
        return s
