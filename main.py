"""Main code module."""

import sys
import os
from random import randint
from arango_orm import Relation, Graph, GraphConnection
from gdb_client import Connection
from db_credentials import (
    db_host, cluster_hosts, db_name, db_port, db_username, db_password)
from models import all_db_objects, Log, Area, Subject, Teacher, Student
import generators

# These constant values are only used for creating valid graph connections.
AREAS_COUNT = 50000
SUBJECTS_COUNT = 20000
STUDENTS_COUNT = 10000000
TEACHERS_COUNT = 100000


def populate_logs(connection, num_recs):
    for i in range(num_recs):
        r = Log(
            _key=generators.uuid(),
            timestamp=generators.random_datetime(),
            message=generators.random_string(randint(10, 200))
        )
        connection.db.add(r)
        if i % 1000 == 0:
            print('.', end='', flush=True)


def populate_areas(connection, num_recs, start_record=1):
    area_number = start_record
    for i in range(num_recs):
        r = Area(_key='Area%i' % area_number)
        connection.db.add(r)
        area_number += 1
        if i % 1000 == 0:
            print('.', end='', flush=True)


def populate_subjects(connection, num_recs, start_record=1):
    subject_number = start_record
    for i in range(num_recs):
        r = Subject(
            _key=str(subject_number),
            name='Subject %i' % subject_number
        )
        connection.db.add(r)
        subject_number += 1
        if i % 1000 == 0:
            print('.', end='', flush=True)


def populate_teachers(connection, num_recs, start_record=1):
    teacher_number = start_record
    for i in range(num_recs):
        r = Teacher(
            _key="T%i" % teacher_number,
            name='Teacher %i' % teacher_number
        )
        connection.db.add(r)
        teacher_number += 1
        if i % 1000 == 0:
            print('.', end='', flush=True)


def populate_students(connection, num_recs, start_record=1):
    student_number = start_record
    for i in range(num_recs):
        r = Student(
            _key="S%i" % student_number,
            name='Student %i' % student_number,
            age=randint(10, 50)
        )
        connection.db.add(r)
        student_number += 1
        if i % 1000 == 0:
            print('.', end='', flush=True)


def set_student_areas(connection, num_recs, start_record=1):
    # db.add(uni_graph.relation(bruce_wayne, Relation("resides_in"), gotham))
    student_number = start_record
    for i in range(num_recs):
        rel = Relation("resides_in")
        rel._from = 'students/S%i' % student_number
        rel._to = 'areas/Area%i' % randint(1, AREAS_COUNT)

        connection.db.add(rel)
        student_number += 1
        if i % 1000 == 0:
            print('.', end='', flush=True)


def set_teacher_areas(connection, num_recs, start_record=1):
    teacher_number = start_record
    for i in range(num_recs):
        rel = Relation("resides_in")
        rel._from = 'teachers/T%i' % teacher_number
        rel._to = 'areas/Area%i' % randint(1, AREAS_COUNT)

        connection.db.add(rel)
        teacher_number += 1
        if i % 1000 == 0:
            print('.', end='', flush=True)


def _generate_edge(edge_type):
    rel_obj = None

    if edge_type == 'student studies subject':
        # select a random student and subject and add a connection
        student_number = randint(1, STUDENTS_COUNT)
        subject_number = randint(1, SUBJECTS_COUNT)
        rel_obj = Relation("studies")

        rel_obj._key = 'S%i_%i' % (student_number, subject_number)
        rel_obj._from = 'students/S%i' % student_number
        rel_obj._to = 'subjects/%i' % subject_number

    elif edge_type == 'teacher teaches subject':
        teacher_number = randint(1, TEACHERS_COUNT)
        subject_number = randint(1, SUBJECTS_COUNT)
        rel_obj = Relation("teaches")

        rel_obj._key = 'T%i_%i' % (teacher_number, subject_number)
        rel_obj._from = 'teachers/T%i' % teacher_number
        rel_obj._to = 'subjects/%i' % subject_number

    return rel_obj


def populate_graph_connections(connection, num_recs):
    recs_inserted = 0
    valid_connections = [
        # GraphConnection(Student, Relation("studies"), Subject),
        'student studies subject',
        # GraphConnection(Teacher, Relation("teaches"), Subject),
        'teacher teaches subject',
    ]

    for i in range(num_recs):
        rtype = valid_connections[randint(0, 1)]
        new_edge = _generate_edge(rtype)
        while connection.db.exists(new_edge):
            new_edge = _generate_edge(rtype)

        connection.db.add(new_edge)
        recs_inserted += 1
        if i % 1000 == 0:
            print('.', end='', flush=True)

    return recs_inserted


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: %s action [parameters]" % sys.argv[0])
        sys.exit(1)

    conn = Connection()
    if os.environ.get('USE_CONNECTION_POOL', False):
        print("Using connection pool")
        conn.cluster_connect(
            cluster_hosts, db_port, db_username, db_password, db_name)
    else:
        conn.connect(db_host, db_port, db_username, db_password, db_name)
    print("Connected to database")

    action = sys.argv[1]

    if 'create_structure' == action:
        conn.create_all(db_objects=all_db_objects)
        print("Structure created!")

    elif 'populate' == action:
        collection = sys.argv[2]
        number_of_records = int(sys.argv[3])
        start_rec = 1
        if len(sys.argv) > 4:
            start_rec = int(sys.argv[4])

        if 'logs' == collection:
            populate_logs(conn, number_of_records)
        elif 'areas' == collection:
            populate_areas(conn, number_of_records, start_rec)
        elif 'subjects' == collection:
            populate_subjects(conn, number_of_records, start_rec)
        elif 'teachers' == collection:
            populate_teachers(conn, number_of_records, start_rec)
        elif 'teacher_areas' == collection:
            set_teacher_areas(conn, number_of_records, start_rec)
        elif 'students' == collection:
            populate_students(conn, number_of_records, start_rec)
        elif 'student_areas' == collection:
            set_student_areas(conn, number_of_records, start_rec)
        elif 'graph_connections' == collection:
            populate_graph_connections(conn, number_of_records)
