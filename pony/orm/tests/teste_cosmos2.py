from __future__ import absolute_import, print_function, division
from pony.py23compat import PYPY2, pickle

import unittest
from datetime import date
from decimal import Decimal

from pony.orm.core import *
from pony.orm.tests.testutils import *

db = Database('cosmosdb', 'https://localhost:8081', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==', 'SchoolDatabase', 'School')

class Student(db.Entity):
    name = Required(unicode)
    scholarship = Optional(int)
    gpa = Optional(Decimal,3,1)
    group = Required('Group')
    dob = Optional(date)

class Group(db.Entity):
    number = PrimaryKey(int)
    students = Set(Student)

db.generate_mapping(create_tables=True)


class TestQuery(unittest.TestCase):
    def setUp(self):
        rollback()
        db_session.__enter__()

    def tearDown(self):
        rollback()
        db_session.__exit__()


    def test1(self):
        with db_session:
            g1 = Group(number=1)
            s1 = Student(id=1, name='S1', group=g1, gpa=3.1)
            s2 = Student(id=2, name='S2', group=g1, gpa=3.2, scholarship=100, dob=date(2000, 1, 1))
            s3 = Student(id=3, name='S3', group=g1, gpa=3.3, scholarship=200, dob=date(2001, 1, 2))
            
            result = Group.select()[:]
            self.assertIsNotNone(result)
            group1 = result[0]
            self.assertEqual(group1.number, g1.number)

            result = Student.select()[:]
            self.assertIsNotNone(result)
            student1 = result[0]
            student2 = result[1]
            student3 = result[2]
            self.assertEqual(student1.id, s1.id)
            self.assertEqual(student1.name, s1.name)
            self.assertEqual(student1.scholarship, s1.scholarship)
            self.assertEqual(student1.gpa, s1.gpa)
            self.assertEqual(student1.group, s1.group)
            self.assertEqual(student1.dob, s1.dob)


if __name__ == '__main__':
    unittest.main()
