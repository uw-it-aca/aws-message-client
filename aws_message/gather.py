import json
from logging import getLogger
from django.conf import settings
from aws_message.aws import SNS, SNSException
from aws_message.sqs import SQSQueue


logger = getLogger(__name__)


class GatherException(Exception):
    pass


class Gather(object):
    """
    Class to gather event messages from AWS SQS queue,
    validate and process their content
    """

    def __init__(self,
                 sqs_settings=None,
                 processor=None,
                 exception=None):
        """
        :param processor: A sub-class of InnerMessageProcessor
        """

        if not processor:
            raise GatherException('missing event processor')

        self._processor = processor

        self._exception = exception if exception \
            else processor.EXCEPTION_CLASS

        self._settings = sqs_settings if sqs_settings \
            else settings.AWS_SQS.get(processor.SETTINGS_NAME)

        self._topicArn = self._settings.get('TOPIC_ARN')

        self._queue = SQSQueue(settings=self._settings)

    def gather_events(self):
        to_fetch = self._settings.get('MESSAGE_GATHER_SIZE')

        while to_fetch > 0:
            messages = self._queue.get_messages(to_fetch)
            for msg in messages:
                try:
                    mbody = json.loads(msg.body)

                    if (self._topicArn is None or
                            mbody['TopicArn'] == self._topicArn):
                        raw_message = SNS(mbody)

                        if self._settings.get('VALIDATE_SNS_SIGNATURE', True):
                            raw_message.validate()

                        if mbody['Type'] == 'Notification':
                            settings = self._settings.get(
                                'PAYLOAD_SETTINGS', {})

                            message = raw_message.extract()

                            self._processor(settings, message).process()

                        elif mbody['Type'] == 'SubscriptionConfirmation':
                            logger.debug(
                                'SubscribeURL: ' + mbody['SubscribeURL'])
                    else:
                        logger.warning(
                            'Unrecognized TopicARN : ' + mbody['TopicArn'])

                except ValueError as err:
                    raise GatherException('JSON : %s' % err)
                except Exception as err:
                    logger.exception("Gather Error")
                    raise GatherException("ERROR: %s MESSAGE: %s" % (err, msg))
                else:
                    message.delete()

            if len(messages) < to_fetch:
                logger.debug("SQS drained")
                break
