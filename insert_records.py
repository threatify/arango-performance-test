"""
Record insertion script.

Wrapper script to run record insertion script inbatch of 10000 records to avoid
the  import script consuming too much memory.
"""

import sys
import os
from util import timeit

MAX_BATCH_SIZE = 10000


@timeit
def import_data():
    """Import Data."""
    records_imported = 0

    cmd = 'python3 main.py ' + ' '.join([sys.argv[1], sys.argv[2]])
    total_records = int(sys.argv[3])

    start_record = 1
    if len(sys.argv) > 4:
        start_record = int(sys.argv[4])

    while records_imported < total_records:
        batch_size = total_records - records_imported
        if batch_size > MAX_BATCH_SIZE:
            batch_size = MAX_BATCH_SIZE

        final_cmd = "%s %i %i" % (cmd, batch_size, start_record)
        print("executing: " + final_cmd)
        exit_code = os.system(final_cmd)
        if 0 == exit_code:
            records_imported += batch_size
        else:
            print("Error: command returned non-zero status")
            sys.exit(1)

        start_record += batch_size

    return records_imported


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s action [parameters]" % sys.argv[0])
        sys.exit(1)

    rec_count = import_data()
    print("Finished! %i records inserted." % rec_count)
