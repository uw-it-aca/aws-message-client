import logging
from abc import ABCMeta, abstractmethod
from django.conf import settings


class ProcessorException(Exception):
    pass


class InnerMessageProcessor(object):
    __metaclass__ = ABCMeta

    def __init__(self, logger,
                 queue_settings_name=None,
                 is_encrypted=False):
        self.logger = logger
        if queue_settings_name:
            self.settings = settings.AWS_SQS.get(queue_settings_name)
        self.is_encrypted = is_encrypted

    def decrypt_inner_message(self, message):
        """
        Override in the sub-class if the inner message is encrypted
        """
        pass

    def extract(self, message):
        if not self.is_encrypted:
            return message

        try:
            return self.decrypt_inner_message(message)
        except Exception as err:
            log_msg = "decrypt_inner_message %s ==> %s" % (message, err)
            self.logger.error(log_msg)
            raise ProcessorException(log_msg)

    def get_payload_setting(self):
        return self.settings.get('PAYLOAD_SETTINGS') if self.settings else None

    def get_queue_setting(self):
        return self.settings

    def process(self, message):
        """
        :param message: the inner message json data
        """
        self.process_inner_message(self.extract(message))

    @abstractmethod
    def process_inner_message(self, json_data):
        """
        A sub-class must define this method
        :raises ProcessorException: any error unable to handle
        """
        pass
