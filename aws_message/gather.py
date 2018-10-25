import json
from logging import getLogger
import traceback
from django.conf import settings
from aws_message.message import (
    SNSException, extract_inner_message, validate_message_signature)
from aws_message.processor import ProcessorException
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
                 processor=None,
                 exception=None,
                 sqs_settings=None):
        """
        :param processor: A sub-class object of InnerMessageProcessor
        """

        if not processor:
            raise GatherException('missing event processor')

        self._processor = processor
        self._settings = sqs_settings if (
            sqs_settings) else self._processor.get_queue_settings()

        self._queue = SQSQueue(self._settings)
        # if Exception, abort!

    def gather_events(self):
        to_fetch = self._settings.get('MESSAGE_GATHER_SIZE')

        while to_fetch > 0:
            messages = self._queue.get_messages(to_fetch)

            if len(messages) == 0:
                logger.info("SQS queue is drained")
                break

            for msg in messages:
                try:
                    mbody = json.loads(msg.body)

                    # common SNS message processing
                    if ('Signature' in mbody and
                            'SignatureVersion' in mbody and
                            'SigningCertURL' in mbody and
                            self._settings.get(
                                'VALIDATE_SNS_SIGNATURE', True)):
                        validate_message_signature(mbody)

                    if ('Type' in mbody and
                            mbody['Type'] == 'SubscriptionConfirmation'):
                        logger.info(
                            'SubscribeURL: {}'.format(
                                mbody['SubscribeURL']))
                    else:
                        self._processor.process(
                            extract_inner_message(mbody))

                except (SNSException, ProcessorException) as err:
                    # log message specific error, abort if unknown error
                    logger.error('{}: {}'.format(
                        err, traceback.format_exc().splitlines()))
                else:
                    msg.delete()
                    # inform the queue that this message has been processed
