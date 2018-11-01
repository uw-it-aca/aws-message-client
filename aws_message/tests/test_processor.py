import logging
from django.test import TestCase, override_settings
from aws_message.processor import MessageBodyProcessor, ProcessorException

logger = logging.getLogger(__name__)


class MockProcessor(MessageBodyProcessor):
    def __init__(self, is_encrypted=False):
        super(MockProcessor, self).__init__(
            logger, queue_settings_name='TEST', is_encrypted=is_encrypted)

        self.event_date = None
        self.href = None
        self.current = None

    def process_message_body(self, json_data):
        self.event_date = json_data['EventDate']
        self.href = json_data['Href']
        self.current = json_data['Current']


class MockInvalidProcessor(MockProcessor):
    def validate_message_body(self, message):
        return False


class UnimplementedProcessor(MessageBodyProcessor):
    pass


M1 = {
    "EventID": "00000000-1111-2222-3333-444444444444",
    "Href": "...",
    "EventDate": "2018-08-12T16:39:08.2704415-07:00",
    "Previous": {
        "CurrentEnrollment": 137,
        "CurrentRegistrationPeriod": "2",
        "Status": "open"},
    "Current": {
        "CurrentEnrollment": 138,
        "CurrentRegistrationPeriod": "2",
        "Status": "open"}
}


class TestUnimplementedProcessor(TestCase):
    @override_settings(AWS_SQS={'TEST': {}})
    def test_process(self):
        self.assertRaises(
            TypeError, UnimplementedProcessor, logger,
            queue_settings_name='TEST')


class TestMockProcessor(TestCase):
    @override_settings(AWS_SQS={'TEST': {}})
    def test_process(self):
        processor = MockProcessor()
        valid = processor.process(M1)
        self.assertEqual(
            processor.event_date, "2018-08-12T16:39:08.2704415-07:00")
        self.assertEqual(
            processor.href, "...")
        self.assertIsNotNone(processor.current)

    @override_settings(AWS_SQS={'TEST': {}})
    def test_process_with_validation(self):
        processor = MockInvalidProcessor(is_encrypted=True)
        valid = processor.process(M1)
        self.assertIsNone(processor.event_date)
        self.assertIsNone(processor.href)
        self.assertIsNone(processor.current)

    @override_settings(AWS_SQS={'TEST': {}})
    def test_process_encrypted(self):
        processor = MockProcessor(is_encrypted=True)
        processor.process(M1)
        self.assertEqual(
            processor.event_date, "2018-08-12T16:39:08.2704415-07:00")
        self.assertEqual(
            processor.href, "...")
        self.assertIsNotNone(processor.current)

    @override_settings(AWS_SQS={'TEST': {'VALIDATE_MSG_SIGNATURE': True}})
    def test_process_with_signature_validation(self):
        processor = MockProcessor()
        processor.process(M1)
        self.assertEqual(
            processor.event_date, "2018-08-12T16:39:08.2704415-07:00")
        self.assertEqual(
            processor.href, "...")
        self.assertIsNotNone(processor.current)
