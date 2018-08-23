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
    "Href": "/v5/course/2018,autumn,MOCK,210/A/status.json",
    "EventDate": "2018-08-12T16:39:08.2704415-07:00",
    "Previous": {
        "CurrentEnrollment": 137,
        "CurrentRegistrationPeriod": "2",
        "AddCodeRequired":  False,
        "FacultyCodeRequired":  False,
        "LimitEstimateEnrollment": 150,
        "LimitEstimateEnrollmentIndicator": "limit",
        "RoomCapacity": 250,
        "Section": {
            "Href": "/v5/course/2018,autumn,MOCK,210/A.json",
            "Year": 2018,
            "Quarter": "autumn",
            "CurriculumAbbreviation": "MOCK",
            "CourseNumber": "210",
            "SectionID": "A",
            "SLN": "12345"},
        "SLN": "12345",
        "SpaceAvailable": 13,
        "Status": "open"},
    "Current": {
        "CurrentEnrollment": 138,
        "CurrentRegistrationPeriod": "2",
        "AddCodeRequired":  False,
        "FacultyCodeRequired":  False,
        "LimitEstimateEnrollment": 150,
        "LimitEstimateEnrollmentIndicator": "limit",
        "RoomCapacity": 250,
        "Section": {
            "Href": "/v5/course/2018,autumn,MOCK,210/A.json",
            "Year": 2018,
            "Quarter": "autumn",
            "CurriculumAbbreviation": "MOCK",
            "CourseNumber": "210",
            "SectionID": "A",
            "SLN": "12345"},
        "SLN": "12345",
        "SpaceAvailable": 12,
        "Status": "open"}
}


class TestMockProcessor(TestCase):

    def test_process(self):
        processor = MockProcessor()
        processor.process(M1)
        self.assertEqual(
            processor.event_date, "2018-08-12T16:39:08.2704415-07:00")
        self.assertEqual(
            processor.href, "/v5/course/2018,autumn,MOCK,210/A/status.json")
        self.assertIsNotNone(processor.current)
