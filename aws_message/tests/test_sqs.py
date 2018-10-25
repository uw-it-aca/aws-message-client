from django.test import TestCase
from aws_message.sqs import SQSQueue


SETTINGS = {
    'TOPIC_ARN': 'arn:aws:sqs:mock:123456789012:ww-wwww-1',
    'KEY_ID': 'XXXXXXXXXXXXXXXX',
    'KEY': 'YYYYYYYYYYYYYYYYYYYYYYYY',
    'VISIBILITY_TIMEOUT': 10,
    'MESSAGE_GATHER_SIZE': 10,
    'VALIDATE_SNS_SIGNATURE': True,
    'PAYLOAD_SETTINGS': {}
}


class TestSQSQueue(TestCase):

    def test_get_queue(self):
        pass
