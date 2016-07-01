import httplib
import socket
import ssl
from boto.sqs.connection import SQSConnection
from boto.sqs.message import RawMessage
from django.conf import settings
from logging import getLogger
from aws_message.aws import SNS, SNSException
import json


class GatherException(Exception):
    pass


class Gather(object):
    """
    Class to gather event messages from AWS SQS queue,
    validate and process their content
    """
    def __init__(self, sqs_settings=None, processor=None, exception=None):
        if not processor:
            raise GatherException('missing event processor')
        else:
            self._processor = processor

        self._exception = exception if exception \
                          else processor.EXCEPTION_CLASS

        self._settings = sqs_settings if sqs_settings \
                         else settings.AWS_SQS.get(processor.SETTINGS_NAME)

        self._topicArn = self._settings.get('TOPIC_ARN')

        connection_kwargs = {
            'aws_access_key_id': self._settings.get('KEY_ID'),
            'aws_secret_access_key': self._settings.get('KEY')
        }

        if (hasattr(self._settings, 'LOCAL_CLIENT_VALIDATION')
            and self._settings.get('LOCAL_CLIENT_VALIDATION')):
            connection_kwargs['https_connection_factory'] = (https_connection_factory, ())

        connection = SQSConnection(**connection_kwargs)

        if connection == None:
            raise GatherException('no connection')

        self._queue = connection.get_queue(self._settings.get('QUEUE'))
        if self._queue == None:
            raise GatherException('no queue')

        self._log = getLogger(__name__)
        self._queue.set_message_class(RawMessage)

    def gather_events(self):
        to_fetch = self._settings.get('MESSAGE_GATHER_SIZE')
        while to_fetch > 0:
            n = min([to_fetch, 10])
            msgs = self._queue.get_messages(
                num_messages=n,
                visibility_timeout=self._settings.get('VISIBILITY_TIMEOUT'))
            for msg in msgs:
                try:
                    sqs_msg = json.loads(msg.get_body())
                    if sqs_msg['TopicArn'] == self._topicArn:
                        aws = SNS(sqs_msg)

                        if self._settings.get('VALIDATE_SNS_SIGNATURE', True):
                            aws.validate()

                        if sqs_msg['Type'] == 'Notification':
                            settings = self._settings.get('PAYLOAD_SETTINGS', {})
                            message = aws.extract()
                            self._processor(settings, message).process()
                        elif sqs_msg['Type'] == 'SubscriptionConfirmation':
                            self._log.debug(
                                'SubscribeURL: ' + sqs_msg['SubscribeURL'])
                    else:
                        self._log.warning(
                            'Unrecognized TopicARN : ' + sqs_msg['TopicArn'])
                except ValueError as err:
                    raise GatherException('JSON : %s' % err)
                except self._exception, err:
                    raise GatherException("MESSAGE: %s" % err)
                except SNSException, err:
                    raise GatherException("SNS: %s" % err)
                except Exception, err:
                    self._log.exception("Gather Error")
                    raise GatherException("ERROR: %s" % err)
                else:
                    self._queue.delete_message(msg)

            if len(msgs) < n:
                self._log.debug("SQS drained")
                break

            to_fetch -= n


class HTTPSConnectionValidating(httplib.HTTPSConnection):
    def __init__(self, host, port=None, key_file=None, cert_file=None, timeout=None, strict=None):
        httplib.HTTPSConnection.__init__(self, host, port=port, key_file=key_file,
                                         cert_file=cert_file, timeout=timeout, strict=strict)
        self.key_file = key_file
        self.cert_file = cert_file
        self.timeout = timeout
        
    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ca_certs=settings.AWS_CA_BUNDLE,
                                    cert_reqs=ssl.CERT_REQUIRED)


def https_connection_factory(host, port=None, strict=None):
    return HTTPSConnectionValidating(host, port=port, strict=strict,
                                     key_file=settings.EVENT_AWS_SQS_KEY,
                                     cert_file=settings.EVENT_AWS_SQS_CERT)
