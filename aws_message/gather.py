from django.conf import settings
from aws_message.aws import SNS, SNSException
from aws_message.sqs import SQSQueue
from logging import getLogger
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

        self._processor = processor
        self._exception = exception if exception \
            else processor.EXCEPTION_CLASS
        self._settings = sqs_settings if sqs_settings \
            else settings.AWS_SQS.get(processor.SETTINGS_NAME)
        self._topicArn = self._settings.get('TOPIC_ARN')
        self._queue = SQSQueue(settings=self._settings)
        self._log = getLogger(__name__)

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
                        raw_message = SNS(sqs_msg)

                        if self._settings.get('VALIDATE_SNS_SIGNATURE', True):
                            raw_message.validate()

                        if sqs_msg['Type'] == 'Notification':
                            settings = self._settings.get(
                                'PAYLOAD_SETTINGS', {})
                            message = raw_message.extract()
                            self._processor(settings, message).process()
                        elif sqs_msg['Type'] == 'SubscriptionConfirmation':
                            self._log.debug(
                                'SubscribeURL: ' + sqs_msg['SubscribeURL'])
                    else:
                        self._log.warning(
                            'Unrecognized TopicARN : ' + sqs_msg['TopicArn'])
                except ValueError as err:
                    raise GatherException('JSON : %s' % err)
                except self._exception as err:
                    raise GatherException("MESSAGE: %s" % err)
                except SNSException as err:
                    raise GatherException("SNS: %s" % err)
                except Exception as err:
                    self._log.exception("Gather Error")
                    raise GatherException("ERROR: %s" % err)
                else:
                    self._queue.delete_message(msg)

            if len(msgs) < n:
                self._log.debug("SQS drained")
                break

            to_fetch -= n
