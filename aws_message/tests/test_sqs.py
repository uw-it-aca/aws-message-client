from django.test.utils import override_settings
from django.test import TestCase
from aws_message.sqs import SQSQueue


old_version = override_settings(
    TOPIC_ARN='arn:aws:sqs:mock:123456789012:ww-wwww-1',
    KEY_ID='XXXXXXXXXXXXXXXX',
    KEY='YYYYYYYYYYYYYYYYYYYYYYYY',
    VISIBILITY_TIMEOUT=10,
    MESSAGE_GATHER_SIZE=10,
    VALIDATE_SNS_SIGNATURE=True,
    PAYLOAD_SETTINGS={}
)
new_version = override_settings(
    ACCOUNT_NUMBER='123456789012',
    QUEUE='ww-wwww-1',
    REGION='xx-xxxx-1',
    KEY_ID='XXXXXXXXXXXXXXXX',
    KEY='YYYYYYYYYYYYYYYYYYYYYYYY',
    VISIBILITY_TIMEOUT=10,
    MESSAGE_GATHER_SIZE=10,
    VALIDATE_SNS_SIGNATURE=True,
    PAYLOAD_SETTINGS={}
)


@old_version
class TestSQSQueue(TestCase):

    def test_get_queue(self):
        pass


@new_version
class TestSQSQueue1(TestCase):

    def test_get_queue(self):
        pass
