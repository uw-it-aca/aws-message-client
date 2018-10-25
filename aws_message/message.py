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


b64encoded = re.compile(r'^[a-zA-Z0-9]+[=]{0,2}$')


def extract_inner_message(mbody):
    message = mbody.get('Message')

    if isinstance(message, dict):
        return message

    if b64encoded.match(message):
        message = b64decode(message)

    return json.loads(message)


def validate_message_signature(mbody):
    """
    raises CryptoException, SNSException
    """
    t = mbody['SignatureVersion']
    if t != '1':
        raise SNSException('Unknown SNS Signature Version: ' + t)

    sig_conf = {
        'cert': {
            'type': 'url',
            'reference': mbody['SigningCertURL']
        }
    }

    try:
        Signature(sig_conf).validate(_signText(mbody),
                                     b64decode(mbody['Signature']))
    except Exception as err:
        raise SNSException('validate_message_body: {} ({})'.format(err, mbody))


def _signText(mbody):
    to_sign = ''
    # see: ("http://docs.amazonwebservices.com/sns/latest/"
    #       "gsg/SendMessageToHttp.verify.signature.html")

    to_sign = _sigElement('Message', mbody) + _sigElement('MessageId', mbody)

    if mbody['Type'] == 'Notification':
        if 'Subject' in mbody:
            to_sign += _sigElement('Subject', mbody)
        to_sign += _sigElement('Timestamp', mbody)

    elif mbody['Type'] == 'SubscriptionConfirmation':
        to_sign += _sigElement('SubscribeURL', mbody)
        to_sign += _sigElement('Timestamp', mbody)
        to_sign += _sigElement('Token', mbody)

    to_sign += _sigElement('TopicArn', mbody)
    to_sign += _sigElement('Type', mbody)

    return to_sign.encode('utf-8')


def _sigElement(el, mbody):
    return '{}\n{}\n'.format(el, mbody[el])


def subscribe(mbody):
    try:
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=settings.AWS_CA_BUNDLE
        )
        r = http.request('GET', mbody['SubscribeURL'])
        if r.status != 200:
            raise SNSException(
                'Subscribe to {} failure: status: {}'.format(
                    mbody['TopicArn'], r.status))
    except urllib3.exceptions.HTTPError as err:
        raise SNSException('Subscribe to {} failure: {}'.format(
            mbody['TopicArn'], err))
