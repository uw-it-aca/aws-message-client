from django.test import TestCase, override_settings
from django.conf import settings
from aws_message.message import Message
from aws_message.crypto import CryptoException

TEST_MESSAGES = [
    {'abc': 'def'},
    'abcdef 123456789',
    '[a, b, c]',
    'TopicArn: nope',
    ['a', 'b', 'c'],
]

TEST_MSG_SNS = {
    'SignatureVersion': '2',
    'Timestamp': '2018-08-22T04:00:56.843Z',
    'Signature': '...',
    'SigningCertURL': '',
    'MessageId': '11111111-0000-1111-2222-555555555555',
    'Message': (
        '{"EventID":"00000000-1111-2222-3333-444444444444","Href":'
        '"...","EventDate":"2018-08-21T21:00:56.832068-07:00","Previous":'
        '{"CurrentEnrollment":19,"Status":"open"},"Current":'
        '{"CurrentEnrollment":20,"Status":"closed"}}'),
    'UnsubscribeURL': '',
    'Type': 'Notification',
    'TopicArn': 'arn:aws:sns:us-east-1:111111111111:test-topic',
    'Subject': 'UW Event',
}

TEST_MSG_SNS_B64 = {
    'SignatureVersion': '1',
    'Timestamp': '2018-08-22T04:00:56.843Z',
    'Signature': '...',
    'SigningCertURL': '',
    'MessageId': '11111111-0000-1111-2222-555555555555',
    'Message': (
        'eyJFdmVudElEIjoiMDAwMDAwMDAtMTExMS0yMjIyLTMzMzMtNDQ0NDQ0NDQ0NDQ0'
        'IiwiSHJlZiI6Ii4uLiIsIkV2ZW50RGF0ZSI6IjIwMTgtMDgtMjFUMjE6MDA6NTYu'
        'ODMyMDY4LTA3OjAwIiwiUHJldmlvdXMiOnsiQ3VycmVudEVucm9sbG1lbnQiOjE5'
        'LCJTdGF0dXMiOiJvcGVuIn0sIkN1cnJlbnQiOnsiQ3VycmVudEVucm9sbG1lbnQi'
        'OjIwLCJTdGF0dXMiOiJjbG9zZWQifX0='),
    'UnsubscribeURL': '',
    'Type': 'Notification',
    'TopicArn': 'arn:aws:sns:us-east-1:111111111111:test-topic',
    'Subject': 'UW Event',
}


class TestMessageExtract(TestCase):
    @override_settings(AWS_SQS={'TEST': {}})
    def test_extract_inner_message_str(self):
        for msg in TEST_MESSAGES:
            message = Message(msg, settings.AWS_SQS['TEST'])
            body = message.extract()
            self.assertEquals(body, msg)

    @override_settings(AWS_SQS={'TEST': {}})
    def test_extract_inner_message_sns_base64(self):
        message = Message(TEST_MSG_SNS_B64, settings.AWS_SQS['TEST'])
        body = message.extract()

        self.assertEquals(
            body["EventID"], '00000000-1111-2222-3333-444444444444')
        self.assertEquals(body["Href"], '...')
        self.assertEquals(
            body["EventDate"], '2018-08-21T21:00:56.832068-07:00')

    @override_settings(AWS_SQS={'TEST': {}})
    def test_extract_inner_message_sns_json(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        body = message.extract()

        self.assertEquals(
            body["EventID"], '00000000-1111-2222-3333-444444444444')
        self.assertEquals(body["Href"], '...')
        self.assertEquals(
            body["EventDate"], '2018-08-21T21:00:56.832068-07:00')


class TestMessageValidate(TestCase):
    @override_settings(AWS_SQS={'TEST': {}})
    def test_validate(self):
        for msg in TEST_MESSAGES:
            message = Message(msg, settings.AWS_SQS['TEST'])
            self.assertEquals(message.validate(), True)

    @override_settings(AWS_SQS={'TEST': {
            'VALIDATE_SNS_SIGNATURE': False,
            'TOPIC_ARN': 'arn:aws:sns:us-east-1:111111111111:test-topic'}},)
    def test_validate_topic_arn(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        self.assertEquals(message.validate(), True)

    @override_settings(AWS_SQS={'TEST': {
            'VALIDATE_SNS_SIGNATURE': False,
            'TOPIC_ARN': 'arn:aws:sns:us-east-1:111111111111:wrong-topic'}},)
    def test_validate_topic_arn_diff(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        self.assertEquals(message.validate(), False)

    @override_settings(AWS_SQS={'TEST': {'VALIDATE_SNS_SIGNATURE': True}},
                       AWS_CA_BUNDLE='ca_certs.txt')
    def test_validate_message_invalid_signature(self):
        message = Message(TEST_MSG_SNS, settings.AWS_SQS['TEST'])
        with self.assertRaises(CryptoException) as cm:
            message.validate()
        self.assertEquals(
            'Unknown SNS Signature Version: 2', str(cm.exception))

    @override_settings(AWS_SQS={'TEST': {'VALIDATE_SNS_SIGNATURE': True}},
                       AWS_CA_BUNDLE='ca_certs.txt')
    def test_validate_message_signature(self):
        message = Message(TEST_MSG_SNS_B64, settings.AWS_SQS['TEST'])
        with self.assertRaises(CryptoException) as cm:
            message.validate()
        self.assertEquals(
            'Cannot get certificate None: No host specified.',
            str(cm.exception))
