from arango_orm.fields import String, Integer, Boolean, DateTime
from arango_orm import Collection, Relation, Graph, GraphConnection


class Student(Collection):
    __collection__ = 'students'

    _key = String(required=True)  # registration number
    name = String(required=True, allow_none=False)
    age = Integer()


class Teacher(Collection):
    __collection__ = 'teachers'

    _key = String(required=True)  # employee id
    name = String(required=True)


class Subject(Collection):
    __collection__ = 'subjects'

    _key = String(required=True)  # subject code
    name = String(required=True)


class Area(Collection):
    __collection__ = 'areas'

    _key = String(required=True)  # area name


class Log(Collection):
    __collection__ = 'logs'

    _key = String(required=True)
    timestamp = DateTime()
    message = String()


class UniversityGraph(Graph):
    __graph__ = 'university_graph'

    graph_connections = [
        # Using general Relation class for relationship
        GraphConnection(Student, Relation("studies"), Subject),
        GraphConnection(Teacher, Relation("teaches"), Subject),
        # Using specific classes for vertex and edges
        GraphConnection([Teacher, Student], Relation("resides_in"), Area)

    ]


all_db_objects = [
    Student, Teacher, Subject, Area, UniversityGraph, Log
]
