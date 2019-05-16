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

with db_session:
    g1 = Group(number=1)
    Student(id=1, name='S1', group=g1, gpa=3.1)
    Student(id=2, name='S2', group=g1, gpa=3.2, scholarship=100, dob=date(2000, 1, 1))
    Student(id=3, name='S3', group=g1, gpa=3.3, scholarship=200, dob=date(2001, 1, 2))


class TestQuery(unittest.TestCase):
    def setUp(self):
        rollback()
        db_session.__enter__()

    def tearDown(self):
        rollback()
        db_session.__exit__()

    def test1(self):
        result = Group.select()[:]
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
