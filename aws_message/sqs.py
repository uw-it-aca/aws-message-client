import boto3
import re
from aws_message.mock_sqs import SQSQueueMock


class SQSException(Exception):
    pass


class SQSQueue(object):

    def __init__(self, sqs_settings):
        self._settings = sqs_settings

        self.queue_name = self._settings.get('QUEUE')
        self.queue_url_pattern = re.compile(
            r"^https://queue.amazonaws.com/%s/%s$" %
            (self._settings.get('ACCOUNT_NUMBER'), self.queue_name))

        try:
            sqs = boto3.resource(
                'sqs',
                aws_access_key_id=self._settings['KEY_ID'],
                aws_secret_access_key=self._settings['KEY'],
                region_name=self._settings['REGION']
            )
            # By default SSL is used
            # By default SSL certificates are verified

            self._queue = sqs.get_queue_by_name(QueueName=self.queue_name)
            if self._queue is None:
                raise SQSException('No queue by name %s' % self.queue_name)

            if self.queue_url_pattern.match(self._queue.url) is None:
                raise SQSException('Invalid queue url %s' % self._queue.url)

        except KeyError as err:
            self._queue = SQSQueueMock(*args, **kwargs)

    def get_messages(self, max_msgs_to_fetch):
        return self._queue.receive_messages(
            AttributeNames=['All'],
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=max_msgs_to_fetch,
            WaitTimeSeconds=self._settings.get('WAIT_TIME', 10),
            VisibilityTimeout=self._settings.get('VISIBILITY_TIMEOUT', 10))

    def delete_message(self, msg):
        raise SQSException('Invalid method for sqs queue')
        # call msg.delete() would delete the message

    def purge_messages(self):
        """
        Delete all the messages in the queue before purge is called
        """
        return self._queue.purge()
