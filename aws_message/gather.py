import json
from logging import getLogger
import traceback
from django.conf import settings
from aws_message.crypto import CryptoException
from aws_message.processor import ProcessorException
from aws_message.sqs import SQSQueue
from aws_message.message import Message


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
        :param processor: A sub-class object of MessageBodyProcessor
        """

        if not processor:
            raise GatherException('missing event processor')

        self._processor = processor
        self._settings = sqs_settings if (
            sqs_settings) else self._processor.get_queue_settings()

        self._queue = SQSQueue(self._settings)
        # if Exception, abort!

    def gather_events(self):
        for msg in self._queue.get_messages():
            try:
                # validate the message and hand it off for processing
                message = Message(json.loads(msg.body), self._settings)
                if message.validate():
                    self._processor.process(message.extract())

            except (CryptoException, ProcessorException) as err:
                # log message specific error, abort if unknown error
                logger.error('{}: {}'.format(
                    err, traceback.format_exc().splitlines()))

            else:
                # inform the queue that this message has been processed
                msg.delete()
