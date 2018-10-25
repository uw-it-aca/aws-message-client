import boto3
import re
from aws_message.mock_sqs import SQSQueueMock


class SQSException(Exception):
    pass


class SQSQueue(object):

    DEFAULT_WAIT_TIME = 10
    DEFAULT_VISIBILITY_TIMEOUT = 10

    def __init__(self, sqs_settings):
        try:
            self._settings = sqs_settings
            self.arn = self._settings.get('TOPIC_ARN')
            self.key_id = self._settings['KEY_ID']
            self.key = self._settings['KEY']
        except KeyError:
            raise SQSException('Invalid SQS configuration {}'.format(
                self._settings))

        # dig region, account and queue_name out of ARN
        #     arn:aws:sqs:<region>:<account-id>:<queuename>
        # defined at:
        #     https://docs.aws.amazon.com/general/latest/
        #         gr/aws-arns-and-namespaces.html
        m = re.match(r'^arn:aws:sqs:'
                     r'(?P<region>([a-z]{2}-[a-z]+-\d+|mock)):'
                     r'(?P<account_id>\d+):'
                     r'(?P<queue_name>[a-z\d\-\_\.]*)$', self.arn, re.I)
        if not m:
            raise SQSException('Invalid ARN: {}'.format(self.arn))

        self.region = m.group('region')
        self.account_id = m.group('account_id')
        self.queue_name = m.group('queue_name')

        if self.region == 'mock':
            self._queue = SQSQueueMock()
            return

        sqs = boto3.resource(
            'sqs',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.key,
            region_name=self.region
        )

        # By default SSL is used
        # By default SSL certificates are verified

        self._queue = sqs.get_queue_by_name(QueueName=self.queue_name)
        if self._queue is None:
            raise SQSException('No queue by name {}'.format(
                self.queue_name))

        if not re.match(r"^https://{}\.[^/]+/{}/{}$".format(
                self.region, self.account_id, self.queue_name),
                        self._queue.url):
            raise SQSException('Invalid queue url {}'.format(self._queue.url))

    def get_messages(self, max_msgs_to_fetch):
        return self._queue.receive_messages(
            AttributeNames=['All'],
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=max_msgs_to_fetch,
            WaitTimeSeconds=self._settings.get(
                'WAIT_TIME', self.DEFAULT_WAIT_TIME),
            VisibilityTimeout=self._settings.get(
                'VISIBILITY_TIMEOUT', self.DEFAULT_VISIBILITY_TIMEOUT))

    def delete_message(self, msg):
        raise SQSException('Invalid method for sqs queue')
        # call msg.delete() would delete the message

    def purge_messages(self):
        """
        Delete all the messages in the queue before purge is called
        """
        return self._queue.purge()
