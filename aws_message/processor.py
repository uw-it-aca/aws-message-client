import logging
from abc import ABC, abstractmethod
from django.conf import settings


class ProcessorException(Exception):
    pass


class MessageBodyProcessor(ABC):
    def __init__(self, logger, queue_settings_name, is_encrypted=False):
        self.logger = logger
        self.settings = settings.AWS_SQS.get(queue_settings_name, {})
        self.is_encrypted = is_encrypted

    def validate_message_body(self, payload):
        """
        Override in the sub-class if the message payload requires validation.
        Must return True or False.
        """
        return True

    def validate_message_body_signature(self, payload):
        """
        Override in the sub-class if the message payload signature requires
        validation.
        """
        pass

    def decrypt_message_body(self, payload):
        """
        Override in the sub-class if the message payload is encrypted
        """
        return payload

    def get_queue_settings(self):
        return self.settings

    def process(self, payload):
        """
        :param payload: the message payload json data
        """
        if self.validate_message_body(payload):

            if self.settings.get('VALIDATE_BODY_SIGNATURE', False):
                self.validate_message_body_signature(payload)

            if self.is_encrypted:
                # the payload is encrypted
                payload = self.decrypt_message_body(payload)

            self.process_message_body(payload)

    @abstractmethod
    def process_message_body(self, payload):
        """
        A sub-class must define this method
        :raises ProcessorException: any error unable to handle
        """
        pass
