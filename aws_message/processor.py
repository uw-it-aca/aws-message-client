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

    def validate_inner_message(self, message):
        """
        Override in the sub-class if the inner message requires validation.
        """
        pass

    def validate_inner_message_signature(self, message):
        """
        Override in the sub-class if the inner message signature requires
        validation.
        """
        pass

    def decrypt_inner_message(self, message):
        """
        Override in the sub-class if the inner message is encrypted
        """
        return message

    def get_payload_settings(self):
        return self.settings.get('PAYLOAD_SETTINGS', {})

    def get_queue_settings(self):
        return self.settings

    def process(self, message):
        """
        :param message: the inner message json data
        """
        self.validate_inner_message(message)

        if self.get_payload_settings().get('VALIDATE_MSG_SIGNATURE', False):
            self.validate_inner_message_signature(message)

        if self.is_encrypted:
            message = self.decrypt_inner_message(message)

        self.process_inner_message(message)

    @abstractmethod
    def process_inner_message(self, json_data):
        """
        A sub-class must define this method
        :raises ProcessorException: any error unable to handle
        """
        pass
