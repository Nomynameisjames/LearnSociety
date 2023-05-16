#!/usr/bin/ env python3
import models
import json
import unittest
from models import storage
from models.baseModel import User, Base, AutoSchedule
from datetime import date, datetime
from models.Schedule import Create_Schedule
from unittest.mock import Mock, patch
from parameterized import parameterized



def PopulatedDB(ID):
    """
        Populates the database with the courses in the json file
    """
    user = Create_Schedule(ID)
    data = user.View(ID, None, "Python")
    if data:
        return
    with open('Python_Courses.json') as f:
        data = json.load(f)
    day = "2023-05-10"
    day = datetime.strptime(day, "%Y-%m-%d").date()
    file = [v for v in data.values()]
    for _, topic in enumerate(file):
        date = day
        task = AutoSchedule(user_ID=str(ID),
                            Days=date,
                            Course=topic["Course"],
                            Topic=topic["Topic"],
                            Target=False,
                            Reminder="18:00:00",
                            Created_at=datetime.utcnow())
        models.storage.new(task)
    models.storage.save()
    return True



class TestCreateSchedule(unittest.TestCase):
    user = Create_Schedule(105)
    def setUp(self):
        """
            Set up the test
            calls the Create_Schedule class to retrieve the user customised
            schedule and the PopulateDB function to populate the database
            automated schedule for a user
        """
        self.ID = 105
        self.auto_schedule = PopulatedDB(self.ID)
        self.schedule = self.user
        self.data = self.schedule.View("105")

    def tearDown(self):
        """
            Tear down the test deletes the user schedule from the database
        """
        models.storage.close()
        #course = ["Python"]
        #self.schedule.DeleteAll(str(self.ID), course)
        #self.schedule.Delete(self.ID)
        del self.schedule

    @parameterized.expand([
        (
            {
                'Day': '2023-05-15',
                'Course': 'Python',
                'Topic': 'Intro to Python',
                'Target': False,
                'Average': None,
                'Reminder': '10:30:00'
            }, True),
        (
            {
                'Day': '2023-05-04',
                'Course': 'C',
                'Topic': 'Functions',
                'Target': False,
                'Average': None,
                'Reminder': "10:30:00"
            }, True)
    ])
    @unittest.skipIf(user.View('105') != {}, "Already created")

    def test_create(self, data, expected):
        """
            test the create method of the Create_Schedule class to create a
            customised schedule for a user
        """
        user = self.schedule.Create(**data)
        save = self.schedule.Save()
        self.assertTrue(save)
        self.assertEqual(save, expected)
        self.assertIsNotNone(self.schedule.user)
        #self.assertEqual(elf.schedule.user, user)
    @unittest.skip("Not implemented yet")
    def test_delete_schedule(self):
        """
            test the delete method of the Create_Schedule class to delete all
            the customised schedule for a user
        """

        data = self.schedule.Delete(self.ID)
        self.assertTrue(data)

    
    @parameterized.expand([
    (105,
     {
        113: {
            'Date': '2023-05-15',
            'Course': 'Python',
            'Topic': 'Intro to Python',
            'Target': True,
            'Average': 50,
            'Reminder': '10:30:00',
            'Created': "2023-05-10 02:55:00",
            'Updated': None
        },
        114: {
            'Date': '2023-05-04',
            'Course': 'C',
            'Topic': 'Functions',
            'Target': True,
            'Average': 40,
            'Reminder': "10:30:00",
            'Created': "2023-05-10 02:55:00",
            'Updated': None
        }
     })
])
    def test_viewAll_schedule(self, ID, expected_result):
        """
            test the view method of the Create_Schedule class to view all the
            customised schedule for a user
        """
        data = self.schedule.View(ID)
        if not data:
            self.assertEqual(data, {})
        else:
            self.assertCountEqual(data.keys(), expected_result.keys())
            for key in data.keys():
                self.assertDictEqual(data[key], expected_result[key])
    
    @parameterized.expand([
        (105, "missed",
         {
             114: {
                 'Date': '2023-05-04',
                 'Course': 'C',
                 'Topic': 'Functions',
                 'Target': True,
                 'Average': 40,
                 'Reminder': "10:30:00",
                 'Created': '2023-05-10 02:55:00',
                 'Updated': None
                 }
             })
         ])
    def test_viewState_schedule(self, ID, state, expected_result):
        """
            test the view method of the Create_Schedule class to view all the
            missed customised schedule of the user
        """
        data = self.schedule.View(ID, state)
        if not data:
            self.assertEqual(data, {})
        else:
            self.assertCountEqual(data.keys(), expected_result.keys())
            for key in data.keys():
                self.assertDictEqual(data[key], expected_result[key])

    @parameterized.expand([
        (105, None, "Python", "Python_Courses.json")
    ])
    def test_viewCourse_schedule(self, ID, state, course, expected_result):
        """
            test the view method of the Create_Schedule class to view all the
            automated schedule of the user
        """
        data = self.schedule.View(ID, state, course)
        if not data:
            self.assertEqual(data, {})
        else:
            with open(expected_result) as f:
                expected_result = json.load(f)
        #self.assertCountEqual(data.keys(), expected_result.keys())
            self.assertEqual(len(data.keys()), len(expected_result.keys()))

    def test_Target(self):
        """
            test the Target method of the Create_Schedule class to view the
            target completion of each course
        """
        data = self.schedule.Target(str(self.ID), "Python")
        false_data = self.schedule.Target(str(self.ID), "C")
        self.assertIsNotNone(data)
        self.assertFalse(false_data[0])
        self.assertIsInstance(data, tuple)
        if data[0]:
            self.assertIsInstance(data[0], float)
        


if __name__ == '__main__':
    unittest.main()
