import logging
from abc import ABC, abstractmethod
from django.conf import settings


class ProcessorException(Exception):
    pass


class InnerMessageProcessor(ABC):
    def __init__(self, logger, queue_settings_name, is_encrypted=False):
        self.logger = logger
        self.settings = settings.AWS_SQS.get(queue_settings_name, {})
        self.is_encrypted = is_encrypted

    def validate_message_body(self, message):
        """
        Override in the sub-class if the inner message requires validation.
        Must return True or False.
        """
        return True

    def validate_message_body_signature(self, message):
        """
        Override in the sub-class if the inner message signature requires
        validation.
        """
        pass

    def decrypt_message_body(self, message):
        """
        Override in the sub-class if the inner message is encrypted
        """
        return message

    def get_queue_settings(self):
        return self.settings

    def process(self, message):
        """
        :param message: the inner message json data
        """
        if self.validate_message_body(message):

            if self.settings.get('VALIDATE_BODY_SIGNATURE', False):
                self.validate_message_body_signature(message)

            if self.is_encrypted:
                message = self.decrypt_message_body(message)

            self.process_message_body(message)

    @abstractmethod
    def process_message_body(self, json_data):
        """
        A sub-class must define this method
        :raises ProcessorException: any error unable to handle
        """
        pass
