import logging
from django.test import TestCase
from aws_message.processor import InnerMessageProcessor


logger = logging.getLogger(__name__)


class MockProcessor(InnerMessageProcessor):

    def __init__(self):
        super(MockProcessor, self).__init__(logger)

    def process_inner_message(self, json_data):
        return json_data['EventDate'], json_data['Href'], json_data['Current']


M1 = {
    "EventID": "0298557a-26fc-49af-9f39-522823e00f2a",
    "Href": "/v5/course/2018,autumn,HCDE,210/A/status.json",
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
            "Href": "/v5/course/2018,autumn,HCDE,210/A.json",
            "Year": 2018,
            "Quarter": "autumn",
            "CurriculumAbbreviation": "HCDE",
            "CourseNumber": "210",
            "SectionID": "A",
            "SLN": "15753"},
        "SLN": "15753",
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
            "Href": "/v5/course/2018,autumn,HCDE,210/A.json",
            "Year": 2018,
            "Quarter": "autumn",
            "CurriculumAbbreviation": "HCDE",
            "CourseNumber": "210",
            "SectionID": "A",
            "SLN": "15753"},
        "SLN": "15753",
        "SpaceAvailable": 12,
        "Status": "open"}
}


class TestMockProcessor(TestCase):

    def test_process(self):
        try:
            processor = MockProcessor()
            event_date, href, current = processor.process_inner_message(M1)
            self.assertEqual(
                event_date, "2018-08-12T16:39:08.2704415-07:00")
            self.assertEqual(
                href, "/v5/course/2018,autumn,HCDE,210/A/status.json")
            self.assertIsNotNone(current)
        except Exception as ex:
            self.fail("TestMockProcessor ERROR: %s" % ex)
