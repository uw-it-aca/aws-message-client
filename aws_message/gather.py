# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from logging import getLogger
import traceback
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
        messages = self._queue.get_messages()
        logger.debug(
            "GATHER: event contains {} messages".format(len(messages)))

        for msg in messages:
            try:
                # validate the message and hand it off for processing
                json_body = json.loads(msg.body)
                logger.debug("GATHER: JSON body: {}".format(json_body))

                message = Message(json_body, self._settings)
                if message.validate():
                    extracted_message = message.extract()
                    logger.debug(
                        "GATHER: processing {}".format(extracted_message))

                    self._processor.process(extracted_message)
                else:
                    logger.debug("GATHER: Message validation failure")

            except (CryptoException, ProcessorException) as err:
                # log message specific error, abort if unknown error
                logger.error('{}: {}'.format(
                    err, traceback.format_exc().splitlines()))

            else:
                # inform the queue that this message has been processed
                msg.delete()
