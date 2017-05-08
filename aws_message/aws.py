"""
Validate and decode AWS SNS/SQS message
"""
from django.conf import settings
import urllib3
import json
import re
from base64 import b64decode
from aws_message.crypto import Signature, CryptoException


class SNSException(Exception):
    pass


class SNS(object):
    """
    Amazon Web Serice SNS Message Class
    """

    _message = None

    def __init__(self, message):
        """
        Amazon Web Service SNS Message object

        Takes an object representing the contents of an AWS SNS message

        Raises SNSException
        """
        self._message = message

    def validate(self):
        t = self._message['SignatureVersion']
        if t != '1':
            raise SNSException('Unknown SNS Signature Version: ' + t)

        sig_conf = {
            'cert': {
                'type': 'url',
                'reference': self._message['SigningCertURL']
            }
        }

        try:
            Signature(sig_conf).validate(
                self._signText(), b64decode(self._message['Signature']))
        except CryptoException as err:
            raise SNSException(
                '%s validation fail: %s' % (self._message['Type'], err))
        except Exception as err:
            raise SNSException(
                'Invalid SNS %s: %s' % (self._message['Type'], err))

    def _signText(self):
        to_sign = ''
        # see: ("http://docs.amazonwebservices.com/sns/latest/"
        #       "gsg/SendMessageToHttp.verify.signature.html")
        to_sign = self._sigElement('Message') + \
            self._sigElement('MessageId')
        if self._message['Type'] == 'Notification':
            if 'Subject' in self._message:
                to_sign += self._sigElement('Subject')

            to_sign += self._sigElement('Timestamp')
        elif self._message['Type'] == 'SubscriptionConfirmation':
            to_sign += self._sigElement('SubscribeURL')
            to_sign += self._sigElement('Timestamp')
            to_sign += self._sigElement('Token')

        to_sign += self._sigElement('TopicArn')
        to_sign += self._sigElement('Type')

        return to_sign.encode('utf-8')

    def _sigElement(self, el):
        return '%s\n%s\n' % (el, self._message[el])

    def extract(self):
        message = self._message['Message']

        if re.match(r'^[a-zA-Z0-9]+[=]{0,2}$', message):
            message = b64decode(message)

        return json.loads(message)

    def subscribe(self):
        try:
            http = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED',
                ca_certs=settings.AWS_CA_BUNDLE
            )
            r = http.request('GET', self._message['SubscribeURL'])
            if r.status != 200:
                raise SNSException(
                    'Subscribe to %s failure: status: %s' % (
                        self._message['TopicArn'], r.status))
        except urllib3.exceptions.HTTPError as err:
            raise SNSException(
                'Subscribe to %s failure: %s' % (
                    self._message['TopicArn'], err))
