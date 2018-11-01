from aws_message.crypto import Signature, CryptoException
from base64 import b64decode
import json
import re

re_base64 = re.compile(
    r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|'
    r'[A-Za-z0-9+/]{3}=)?$')


class Message(object):
    def __init__(self, message, settings):
        self._message = message
        self._settings = settings
        self._is_sns = (isinstance(message, dict) and 'TopicArn' in message)

    def validate(self):
        valid = True
        if self._is_sns:
            # SNS message validation
            valid = self._validate_topic_arn()

            if valid and self._settings.get('VALIDATE_SNS_SIGNATURE', True):
                self._validate_sns_signature()

        return valid

    def extract(self):
        message = self._message
        if self._is_sns:
            message = message.get('Message')

        if not isinstance(message, str):
            return message

        if re_base64.match(message):
            message = b64decode(message)

        try:
            return json.loads(message)
        except json.decoder.JSONDecodeError:
            return message

    def _validate_topic_arn(self):
        if (self._settings.get('TOPIC_ARN') and
                self._message['TopicArn'] != self._settings['TOPIC_ARN']):
            return False
        return True

    def _validate_sns_signature(self):
        if self._message['SignatureVersion'] != '1':
            raise CryptoException('Unknown SNS Signature Version: {}'.format(
                self._message['SignatureVersion']))

        sig_conf = {
            'cert': {
                'type': 'url',
                'reference': self._message['SigningCertURL']
            }
        }

        Signature(sig_conf).validate(self._sign_text(self._message),
                                     b64decode(self._message['Signature']))

    @staticmethod
    def _sign_text(message):
        """
        Reference:
        https://docs.aws.amazon.com/sns/latest/dg/SendMessageToHttp.verify.signature.html
        """
        to_sign = ''

        def sig_pair(el, message):
            return '{}\n{}\n'.format(el, message[el])

        to_sign = sig_pair('Message', message)
        to_sign += sig_pair('MessageId', message)

        if message['Type'] == 'Notification':
            if 'Subject' in message:
                to_sign += sig_pair('Subject', message)
            to_sign += sig_pair('Timestamp', message)

        elif message['Type'] == 'SubscriptionConfirmation':
            to_sign += sig_pair('SubscribeURL', message)
            to_sign += sig_pair('Timestamp', message)
            to_sign += sig_pair('Token', message)

        to_sign += sig_pair('TopicArn', message)
        to_sign += sig_pair('Type', message)

        return to_sign.encode('utf-8')
