import logging
from django.test import TestCase
from aws_message.processor import InnerMessageProcessor


logger = logging.getLogger(__name__)


class MockProcessor(InnerMessageProcessor):

    def __init__(self):
        super(MockProcessor, self).__init__(logger)

    def process_inner_message(self, json_data):
        self.event_date = json_data['EventDate']
        self.href = json_data['Href']
        self.current = json_data['Current']


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


class TestMockProcessor(TestCase):

    def test_process(self):
        processor = MockProcessor()
        processor.process(M1)
        self.assertEqual(
            processor.event_date, "2018-08-12T16:39:08.2704415-07:00")
        self.assertEqual(
            processor.href, "...")
        self.assertIsNotNone(processor.current)
