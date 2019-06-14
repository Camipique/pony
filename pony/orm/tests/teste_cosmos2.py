from __future__ import absolute_import, print_function, division

import unittest
from datetime import datetime
from decimal import Decimal

from pony.orm.core import *
from pony.orm.tests.testutils import *

db = Database('cosmosdb',
              'https://localhost:8081',
              'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==',
              'SchoolDatabase',
              'School')


class Student(db.Entity):
    student_id = PrimaryKey(int)
    name = Required(unicode)
    scholarship = Optional(int)
    gpa = Optional(Decimal, 3, 1)
    group = Required('Group')
    dob = Optional(datetime)
    extra = Optional(Json)


class Group(db.Entity):
    number = PrimaryKey(int)
    name = Required(unicode)
    students = Set(Student)
    extra = Optional(Json)


db.generate_mapping(create_tables=True)

with db_session:
    g1 = Group(number=1, name="group1", extra={"chave1": "valor1", "chave2": 2})
    g2 = Group(number=2, name="group2", extra={"chave1": "valor2", "chave2": {"chave3": 3}})
    s1 = Student(student_id=1, name='S1', group=g1, gpa=3.1)
    s2 = Student(student_id=2, name='S2', group=g1, gpa=3.2, scholarship=100, dob=datetime(2010, 1, 1))
    s3 = Student(student_id=3, name='S3', group=g1, gpa=3.3, scholarship=200, dob=datetime(2001, 1, 2))


class TestQuery(unittest.TestCase):
    def setUp(self):
        rollback()
        db_session.__enter__()

    def tearDown(self):
        rollback()
        db_session.__exit__()

    def test_simple_condition(self):
        with db_session:
            # Simple select with conditions
            result = Group.select(lambda g: g.number == 1)[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            for g in result:
                self.assertEqual(g.number, 1)

            result = Group.select(lambda g: g.name == "group1")[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            for g in result:
                self.assertIsNotNone(g.name, "group1")

            result = Student.select(lambda s: s.gpa > Decimal('3.1'))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            for s in result:
                self.assertGreater(s.gpa, 3.1)

    def test_select_all(self):
        with db_session:
            # Select all groups
            result = Group.select()[:]
            self.assertIsNotNone(result)

            group1 = result[0]
            group2 = result[1]

            self.assertEqual(group1.number, g1.number)
            self.assertEqual(group1.name, g1.name)
            self.assertEqual(group1.extra, g1.extra)

            self.assertEqual(group2.number, g2.number)
            self.assertEqual(group2.name, g2.name)
            self.assertEqual(group2.extra, g2.extra)

            # Select all students
            result = Student.select()[:]
            self.assertIsNotNone(result)

            student1 = result[0]
            student2 = result[1]
            student3 = result[2]

            self.assertEqual(s1.student_id, student1.student_id)
            self.assertEqual(s1.name, student1.name)
            self.assertEqual(s1.group.name, student1.group.name)
            self.assertEqual(s1.gpa, student1.gpa)
            self.assertEqual(s1.extra, student1.extra)

            self.assertEqual(s2.student_id, student2.student_id)
            self.assertEqual(s2.name, student2.name)
            self.assertEqual(s2.group.name, student2.group.name)
            self.assertEqual(s2.gpa, student2.gpa)
            self.assertEqual(s2.scholarship, student2.scholarship)
            self.assertEqual(s2.dob, student2.dob)
            self.assertEqual(s2.extra, student2.extra)

            self.assertEqual(s3.student_id, student3.student_id)
            self.assertEqual(s3.name, student3.name)
            self.assertEqual(s3.group.name, student3.group.name)
            self.assertEqual(s3.gpa, student3.gpa)
            self.assertEqual(s3.scholarship, student3.scholarship)
            self.assertEqual(s3.dob, student3.dob)
            self.assertEqual(s3.extra, student3.extra)

    def test_pk(self):
        with db_session:
            def get_group_by_pk(_id):
                return Group[_id]

            def get_student_by_pk(_id):
                return Student[_id]

            result = get_student_by_pk(2)
            self.assertIsNotNone(result)

            student2 = result

            self.assertEqual(s2.student_id, student2.student_id)
            self.assertEqual(s2.name, student2.name)
            self.assertEqual(s2.group.name, student2.group.name)
            self.assertEqual(s2.gpa, student2.gpa)
            self.assertEqual(s2.scholarship, student2.scholarship)
            self.assertEqual(s2.dob, student2.dob)
            self.assertEqual(s2.extra, student2.extra)

            # Try to get a non existent student, using primary key
            self.assertRaises(pony.orm.core.ObjectNotFound, get_student_by_pk, 4)

            result = get_group_by_pk(1)
            self.assertIsNotNone(result)

            group1 = result

            self.assertEqual(group1.number, g1.number)
            self.assertEqual(group1.name, g1.name)
            self.assertEqual(group1.extra, g1.extra)

            # Try to get a non existent group, using primary key
            self.assertRaises(pony.orm.core.ObjectNotFound, get_group_by_pk, 3)

    def test_dict_queries(self):
        with db_session:
            # Query using dictionary values
            result = Group.select(lambda g: g.extra['chave2']['chave3'] == 3)[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            for g in result:
                self.assertEqual(g.extra['chave2']['chave3'], 3)

            result = Group.select(lambda g: g.extra['chave1'] == 'valor1')[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            for g in result:
                self.assertEqual(g.extra['chave1'], 'valor1')

            result = Group.select(lambda g: g.extra['chave2']['not_defined'] == 'not_defined')[:]
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 0)

    def test_datetime_queries(self):
        with db_session:
            # Datetime

            result = Student.select(lambda s: s.dob > datetime(1990, 1, 1) and s.dob < datetime(2002, 1, 1))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            self.assertEqual(result[0].dob, datetime(2001, 1, 2))

            result = Student.select(lambda s: s.dob < datetime(2002, 1, 1) and s.dob > datetime(1990, 1, 1))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            self.assertEqual(result[0].dob, datetime(2001, 1, 2))

    def test_aggregate_queries(self):
        with db_session:
            pass
            # # Aggregation
            #
            # result = sum(s.scholarship for s in Student)[:]
            # self.assertIsNotNone(result)
            #
            # result = avg(s.scholarship for s in Student)[:]
            # self.assertIsNotNone(result)

    def test_in_queries(self):
        with db_session:
            # Queries using IN clause
            result = Student.select(lambda s: s.name in ('S1', 'S2'))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            self.assertEqual(result[0].name, 'S1')
            self.assertEqual(result[1].name, 'S2')

            result = Student.select(lambda s: s.gpa in (Decimal('3.1'), Decimal('3.2')))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            self.assertEqual(result[0].gpa, Decimal('3.1'))
            self.assertEqual(result[1].gpa, Decimal('3.2'))

            result = Student.select(lambda s: s.dob in (datetime(2010, 1, 1), datetime(2001, 1, 2)))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            self.assertEqual(result[0].dob, datetime(2010, 1, 1))
            self.assertEqual(result[1].dob, datetime(2001, 1, 2))

# Queries with relation between objects
# result = Student.select(lambda s: s.group.number == g1.number)
#
# for s in result:
#     self.assertEqual(s.group.number, g1.number)
#     self.assertEqual(s.group.name, g1.name)
#
# result = Student.select(lambda s: s.group.name == g1.name)
#
# for s in result:
#     self.assertEqual(s.group.number, g1.number)
#     self.assertEqual(s.group.name, g1.name)
#
# result = Student.select(lambda s: s.group.number == g2.number)
#
# for s in result:
#     self.assertEqual(s.group.number, g1.number)


if __name__ == '__main__':
    unittest.main()
