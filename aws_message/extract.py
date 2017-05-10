"""
Extract - Base class to pull body out of AWS message
"""
from aws_message.crypto import aes128cbc, Signature, CryptoException
from base64 import b64decode
import json


class ExtractException(Exception):
    pass


class Extract(object):
    """
    Base class to extract AWS message contents
    """
    def __init__(self, config, message):

        self._settings = config
        self._header = message['header']
        self._body = message['body']

    def extract(self):
        return self.parse(self._header['contentType'].lower(),
                          self._raw_message())

    def parse(self, content_type, body):
        if content_type == 'json':
            return json.loads(body)

        raise ExtractException('Unknown content-type: %s' % (content_type))

    def _raw_message(self):
        if self._settings.get('VALIDATE_MSG_SIGNATURE', True):
            self._validate()

        body = b64decode(self._body)

        try:
            if set(['keyId', 'iv']).issubset(self._header):
                key = self._header['keyId']
                keys = self._settings.get('KEYS', {})
                if key not in keys:
                    raise ExtractException('Invalid keyId : %s' (key))

                cipher = aes128cbc(b64decode(keys[key]),
                                   b64decode(self._header['iv']))
                body = cipher.decrypt(body)
        except CryptoException as err:
            raise ExtractException('Cannot decrypt: %s' % (err))
        except Exception as err:
            raise ExtractException('Cannot read: %s' % (err))

        return body

    def _validate(self):
        to_sign = self._header[u'contentType'] + '\n'
        if 'keyId' in self._header:
            to_sign += self._header[u'iv'] + '\n' + \
                       self._header[u'keyId'] + '\n'
        to_sign += self._header[u'messageContext'] + '\n' + \
            self._header[u'messageId'] + '\n' + \
            self._header[u'messageType'] + '\n' + \
            self._header[u'sender'] + '\n' + \
            self._header[u'signingCertUrl'] + '\n' + \
            self._header[u'timestamp'] + '\n' + \
            self._header[u'version'] + '\n' + \
            self._body + '\n'

        sig_conf = {
            'cert': {
                'type': 'url',
                'reference': self._header[u'signingCertUrl']
            }
        }

        try:
            Signature(sig_conf).validate(to_sign.encode('ascii'),
                                         b64decode(self._header['signature']))
        except CryptoException as err:
            raise ExtractException('Cannot unencode message: %s' % (err))
        except Exception as err:
            raise ExtractException('Invalid signature %s: %s' (
                self._header['signature'], err))
