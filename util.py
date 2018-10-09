"""Utility code."""

import time


def timeit(method):
    """Time the execution of a call."""
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) took %2.2f seconds' %
              (method.__name__, args, kw, te-ts))

        return result

    return timed


def new_rec(col_class, **kwargs):
    obj = col_class()
    for k, v in kwargs.items():
        setattr(obj, k, v)

    return obj


def get_collection_class(collection_name, db_objects):
    for dbo in db_objects:
        if hasattr(dbo, '__collection__') \
           and dbo.__collection__ == collection_name:

            return dbo

    return None
