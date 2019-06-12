from __future__ import absolute_import, print_function, division

import unittest
from datetime import datetime
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
    dob = Optional(datetime)
    extra = Optional(Json)


class Group(db.Entity):
    number = PrimaryKey(int)
    name = Required(unicode)
    students = Set(Student)
    extra = Optional(Json)


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
            s3_dob = datetime(2001, 1, 2)

            g1 = Group(number=1, name="group1", extra={"chave1": "valor1", "chave2": 2})
            g2 = Group(number=2, name="group2", extra={"chave1": "valor2", "chave2": { "chave3": 3}})
            s1 = Student(id=1, name='S1', group=g1, gpa=3.1)
            s2 = Student(id=2, name='S2', group=g1, gpa=3.2, scholarship=100, dob=datetime(2010, 1, 1))
            s3 = Student(id=3, name='S3', group=g1, gpa=3.3, scholarship=200, dob=s3_dob)

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

            # PK

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

            # Datetime

            result = Student.select(lambda s: s.dob > datetime(1990, 1, 1) and s.dob < datetime(2002, 1, 1))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            self.assertEqual(result[0].dob, s3_dob)

            result = Student.select(lambda s: s.dob < datetime(2002, 1, 1) and s.dob > datetime(1990, 1, 1))[:]
            self.assertIsNotNone(result)
            self.assertNotEqual(len(result), 0)

            self.assertEqual(result[0].dob, s3_dob)

            # Aggregation

            # result = sum(s.scholarship for s in Student)[:]
            # self.assertIsNotNone(result)

            # result = avg(s.scholarship for s in Student)[:]
            # self.assertIsNotNone(result)

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
