from django.test import TestCase
from aws_message.sqs import SQSQueue, SQSException


class MockQueue(object):
    def receive_messages(self, **kwargs):
        return [''] * kwargs.get('MaxNumberOfMessages')


class MockEmptyQueue(MockQueue):
    def receive_messages(self, **kwargs):
        return []


class TestSQSQueue(TestCase):
    def setUp(self):
        self._mock_settings = {
            'QUEUE_ARN': 'arn:aws:sqs:xx-mock-999:000000000000:ww-wwww-1',
            'KEY_ID': 'XXXXXXXXXXXXXXXX',
            'KEY': 'YYYYYYYYYYYYYYYYYYYYYYYY',
            'WAIT_TIME': 10,
            'VISIBILITY_TIMEOUT': 10,
            'MESSAGE_GATHER_SIZE': 10,
            'POLL_COUNT': 10,
        }

        self.sqs = SQSQueue(self._mock_settings)
        self.sqs._queue = MockQueue()

    def test_queue(self):
        self.assertEquals(
            self.sqs.arn, 'arn:aws:sqs:xx-mock-999:000000000000:ww-wwww-1')
        self.assertEquals(self.sqs.key_id, 'XXXXXXXXXXXXXXXX')
        self.assertEquals(self.sqs.key, 'YYYYYYYYYYYYYYYYYYYYYYYY')
        self.assertEquals(self.sqs.region, 'xx-mock-999')
        self.assertEquals(self.sqs.account_id, '000000000000')
        self.assertEquals(self.sqs.queue_name, 'ww-wwww-1')

        #  Overridden __getattr__ should still raise an AttributeError
        self.assertRaises(AttributeError, lambda: self.sqs._does_not_exist)

    def test_get_messages(self):
        messages = self.sqs.get_messages()
        self.assertEquals(len(messages), 100)

        self.sqs._settings['MESSAGE_GATHER_SIZE'] = 9
        messages = self.sqs.get_messages()
        self.assertEquals(len(messages), 90)

        self.sqs._settings['POLL_COUNT'] = 1
        messages = self.sqs.get_messages()
        self.assertEquals(len(messages), 9)

    def test_empty_queue(self):
        self.sqs._queue = MockEmptyQueue()
        messages = self.sqs.get_messages()
        self.assertEquals(len(messages), 0)


class TestSQSQueueErrors(TestCase):
    def test_queue_errors(self):
        missing_settings = {}
        with self.assertRaises(SQSException) as context:
            sqs = SQSQueue(missing_settings)
        self.assertIn(
            'Invalid SQS configuration', str(context.exception))

        invalid_settings = {
            'QUEUE_ARN': 'abc',
            'KEY_ID': '',
            'KEY': '',
        }
        with self.assertRaises(SQSException) as context:
            sqs = SQSQueue(invalid_settings)
        self.assertIn('Invalid ARN', str(context.exception))
