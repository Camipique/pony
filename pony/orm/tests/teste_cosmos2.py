from __future__ import absolute_import, print_function, division

import unittest
from datetime import date
from decimal import Decimal

from pony.orm.core import *
from pony.orm.tests.testutils import *

db = Database('cosmosdb', 'https://localhost:8081', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==', 'SchoolDatabase', 'School')


class Student(db.Entity):
    id = PrimaryKey(int)
    name = Required(unicode)
    scholarship = Optional(int)
    gpa = Optional(Decimal, 3, 1)
    group = Required('Group')
    dob = Optional(date)


class Group(db.Entity):
    number = PrimaryKey(int)
    name = Required(unicode)
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
            g1 = Group(number=1, name="group1")
            g2 = Group(number=2, name="group2")
            s1 = Student(id=1, name='S1', group=g1, gpa=3.1)
            s2 = Student(id=2, name='S2', group=g1, gpa=3.2, scholarship=100, dob=date(2000, 1, 1))
            s3 = Student(id=3, name='S3', group=g1, gpa=3.3, scholarship=200, dob=date(2001, 1, 2))

            # Select all groups
            result = Group.select()[:]
            self.assertIsNotNone(result)

            group1 = result[0]

            self.assertEqual(group1.number, g1.number)

            # Select all students
            result = Student.select()[:]
            self.assertIsNotNone(result)

            student1 = result[0]
            student2 = result[1]
            student3 = result[2]

            self.assertEqual(s1, student1)
            self.assertEqual(s2, student2)
            self.assertEqual(s3, student3)

            # Simple select with conditions
            result = Group.select(lambda g: g.number == 1)[:]
            self.assertIsNotNone(result)

            for g in result:
                self.assertEqual(g.number, 1)

            result = Student.select(lambda s: s.gpa > Decimal('3.1'))[:]
            self.assertIsNotNone(result)

            for s in result:
                self.assertGreater(s.gpa, 3.1)

            def get_group_by_pk(_id):
                return Group[_id]

            def get_student_by_pk(_id):
                return Student[_id]

            # Get student object by primary key
            result = get_student_by_pk(2)
            self.assertIsNotNone(result)

            self.assertEqual(s2, result)

            # Try to get a non existent student, using primary key
            self.assertRaises(pony.orm.core.ObjectNotFound, get_student_by_pk, 4)

            # Get group object by primary key
            result = get_group_by_pk(1)
            self.assertIsNotNone(result)

            self.assertEqual(g1, result)

            # Try to get a non existent group, using primary key
            self.assertRaises(pony.orm.core.ObjectNotFound, get_group_by_pk, 3)

            # Queries with relation between objects
            result = Student.select(lambda s: s.group.number == g1.number)

            for s in result:
                self.assertEqual(s.group.number, g1.number)
                self.assertEqual(s.group.name, g1.name)

            result = Student.select(lambda s: s.group.name == g1.name)

            for s in result:
                self.assertEqual(s.group.number, g1.number)
                self.assertEqual(s.group.name, g1.name)

            result = Student.select(lambda s: s.group.number == g2.number)

            for s in result:
                self.assertEqual(s.group.number, g1.number)


if __name__ == '__main__':
    unittest.main()
