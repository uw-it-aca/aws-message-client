import logging
import re


class ProcessorException(Exception):
    pass


class InnerMessageProcessor(object):

    SETTINGS_NAME = None
    EXCEPTION_CLASS = ProcessorException

    def __init__(self, logger, message, is_encrypted=False):
        """
        :param message: a dict representing a UW Course Event Inner Message
        Raises EventException
        """
        self.logger = logger
        self.is_encrypted = is_encrypted
        self.message = message
        self.logger.debug(message)

    def decrypt_inner_message(self):
        """
        if the inner message is encrypted, decrypt the message body
        """
        pass

    def extract(self):
        if not self.is_encrypted:
            return self.message

        try:
            return self.decrypt_inner_message()
        except Exception as err:
            raise ProcessorException("decrypt_inner_message %s ==> %s" %
                                     (self.message, err))

    def process(self):
        self.process_inner_message(self.extract())

    def process_inner_message(self, json_data):
        """
        A sub-class must define this method
        """
        raise ProcessorException('Please define process method')
