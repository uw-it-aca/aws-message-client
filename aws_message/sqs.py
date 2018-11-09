import boto3
import re


class SQSException(Exception):
    pass


class SQSQueue(object):

    DEFAULT_WAIT_TIME = 10
    DEFAULT_VISIBILITY_TIMEOUT = 10
    DEFAULT_MESSAGE_GATHER_SIZE = 10
    DEFAULT_POLL_COUNT = 1

    def __init__(self, sqs_settings):
        try:
            self._settings = sqs_settings
            self.arn = self._settings.get('QUEUE_ARN')
            self.key_id = self._settings['KEY_ID']
            self.key = self._settings['KEY']
        except KeyError as ex:
            raise SQSException(
                'Invalid SQS configuration: Missing {}'.format(ex))

        # dig region, account and queue_name out of ARN
        #     arn:aws:sqs:<region>:<account-id>:<queuename>
        # defined at:
        #     https://docs.aws.amazon.com/general/latest/
        #         gr/aws-arns-and-namespaces.html
        m = re.match(r'^arn:aws:sqs:'
                     r'(?P<region>([a-z]{2}-[a-z]+-\d+)):'
                     r'(?P<account_id>\d+):'
                     r'(?P<queue_name>[a-z\d\-\_\.]*)$', self.arn, re.I)
        if not m:
            raise SQSException('Invalid ARN: {}'.format(self.arn))

        self.region = m.group('region')
        self.account_id = m.group('account_id')
        self.queue_name = m.group('queue_name')

    def __getattr__(self, attr):
        if attr == '_queue':
            sqs = boto3.resource(
                'sqs',
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.key,
                region_name=self.region
            )

            self._queue = sqs.get_queue_by_name(QueueName=self.queue_name)
            if self._queue is None:
                raise SQSException('No queue by name {}'.format(
                    self.queue_name))
            return self._queue
        raise AttributeError(attr)

    def get_messages(self):
        ret_messages = []
        poll_count = self._settings.get('POLL_COUNT', self.DEFAULT_POLL_COUNT)
        for i in range(poll_count):
            messages = self._queue.receive_messages(
                AttributeNames=['All'],
                MessageAttributeNames=['All'],
                MaxNumberOfMessages=self._settings.get(
                    'MESSAGE_GATHER_SIZE', self.DEFAULT_MESSAGE_GATHER_SIZE),
                WaitTimeSeconds=self._settings.get(
                    'WAIT_TIME', self.DEFAULT_WAIT_TIME),
                VisibilityTimeout=self._settings.get(
                    'VISIBILITY_TIMEOUT', self.DEFAULT_VISIBILITY_TIMEOUT))

            ret_messages.extend(messages)
            if not len(messages):
                break

        return ret_messages
