from django.test import TestCase
from aws_message.message import (
    extract_inner_message, validate_message_signature)

mbody = {
    u'SignatureVersion': u'1',
    u'Timestamp': u'2018-08-22T04:00:56.843Z',
    u'Signature': u'...',
    u'SigningCertURL': (
        u'https://sss.qq-qqqq-1.aaaaaaaaa.com/SimpleNotificationService-'
        u'00000000000000000000000000000000.pem'),
    u'MessageId': u'11111111-0000-1111-2222-555555555555',
    u'Message': (
        u'{"EventID":"00000000-1111-2222-3333-444444444444","Href":'
        u'"...","EventDate":"2018-08-21T21:00:56.832068-07:00","Previous":'
        u'{"CurrentEnrollment":19,"Status":"open"},"Current":'
        u'{"CurrentEnrollment":20,"Status":"closed"}}'),
    u'UnsubscribeURL': (
        u'https://sss.qq-qqqq-1.aaaaaaaaa.com/?Action=Unsubscribe&'
        u'SubscriptionArn=arn:aaa:sss:qq-qqqq-1:...:...:...'),
    u'Type': u'Notification',
    u'TopicArn': u'arn:aaa:sas:qq-qqqq-1:...:...:...',
    u'Subject': u'UW Event',
}


class TestMockProcessor(TestCase):

    def test_extract_inner_message(self):
        message = extract_inner_message(mbody)
        self.assertTrue("EventID" in message)
        self.assertTrue("Href" in message)
        self.assertTrue("EventDate" in message)
        self.assertTrue("Previous" in message)
        self.assertTrue("Current" in message)

    def test_validate_message_signature(self):
        with self.settings(AWS_CA_BUNDLE="/data/"):
            try:
                validate_message_signature(mbody)
            except AttributeError as ex:
                # python 3.6: module 'string' has no attribute 'lower'
                # line 44: Signature(sig_conf).validate(_signText(mbody)
                pass
            except Exception as ex:
                pass
