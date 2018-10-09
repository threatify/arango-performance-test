"""Main code module."""

import sys
from random import randint
from gdb_client import Connection
from db_credentials import db_host, db_name, db_port, db_username, db_password
from models import all_db_objects, Log
from util import get_collection_class, new_rec, timeit
import generators


@timeit
def populate_logs(db, num_recs):
    for i in range(num_recs):
        r = Log(
            _key=generators.uuid(),
            timestamp=generators.random_datetime(),
            message=generators.random_string(randint(10, 200))
        )
        db.add(r)
        if i % 1000 == 0:
            print('.', end='', flush=True)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: %s action [parameters]" % sys.argv[0])
        sys.exit(1)

    conn = Connection()
    conn.connect(db_host, db_port, db_username, db_password, db_name)
    print("Connected to database")

    action = sys.argv[1]

    if 'create_structure' == action:
        conn.create_all(db_objects=all_db_objects)
        print("Structure created!")

    elif 'populate' == action:
        collection = sys.argv[2]
        number_of_records = int(sys.argv[3])
        if 'logs' == collection:
            populate_logs(conn.db, number_of_records)
