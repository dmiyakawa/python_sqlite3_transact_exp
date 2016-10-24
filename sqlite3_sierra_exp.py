#!/usr/bin/env python

"""\
An example that crashes on macOS Sierra.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG
from multiprocessing import Process, freeze_support
from threading import Thread
import os
import sqlite3
import sys
import time

_DB_PATH = os.path.join(os.path.dirname(__file__), 'state.db')


def _connect(db_path):
    conn = sqlite3.connect(db_path)
    return conn


def get_count(db_path,  name):
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute('''\
    SELECT count FROM test_table
    WHERE name = ?
    ''', (name,))
    (count,) = c.fetchone()
    conn.commit()
    conn.close()
    return count


def incrementer_process(db_path, name):
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute('''\
    SELECT count FROM test_table
    WHERE name = ?
    ''', (name,))
    (count,) = c.fetchone()
    c.execute('''\
    INSERT OR REPLACE INTO test_table
    (name, count)
    VALUES (?, ?)
    ''', (name, count + 1))
    conn.commit()
    conn.close()


def main():
    logger = getLogger(__name__)
    handler = StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter('%(asctime)s %(message)s'))
    logger.info('python version: {}'.format(sys.version))
    logger.info('module_version: {}'.format(sqlite3.version))
    logger.info('sqlite3_version: {}'.format(sqlite3.sqlite_version))
    name = 'name'
    db_path = _DB_PATH
    conn = _connect(db_path)
    c = conn.cursor()
    c.execute('''\
    DROP TABLE IF EXISTS
    test_table
    ''')
    c.execute('''\
    CREATE TABLE IF NOT EXISTS
    test_table (name text, count integer)
    ''')
    c.execute('''\
    CREATE UNIQUE INDEX IF NOT EXISTS
    files_index ON test_table (name)
    ''')
    c.execute('''\
    INSERT OR REPLACE INTO test_table
    (name, count)
    VALUES (?, ?)
    ''', (name, 0))
    conn.commit()
    conn.close()
    logger.debug('Creating a child')
    child = Process(target=incrementer_process,
                    args=(db_path, name))
    #child = Thread(target=incrementer_process,
    #           args=process_args,
    #           kwargs=process_kwargs)
    child.start()
    child.join()
    logger.info('value: {}'.format(get_count(db_path, name)))


if __name__ == '__main__':
    freeze_support()
    main()
