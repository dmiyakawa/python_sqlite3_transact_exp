#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""\
Describe your program here
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from logging import getLogger, StreamHandler, Formatter
from logging import NOTSET, DEBUG, INFO, WARN, ERROR, CRITICAL
import multiprocessing
from threading import Thread
import os
import sqlite3
import sys
import time


_LOG_LEVELS = {'NOTSET': NOTSET, 'DEBUG': DEBUG, 'INFO': INFO, 'WARN': WARN,
               'ERROR': ERROR, 'CRITICAL': CRITICAL}

_DB_PATH = os.path.join(os.path.dirname(__file__), 'state.db')


def _connect(db_path, isolation_level):
    conn = sqlite3.connect(db_path, isolation_level=isolation_level)
    return conn


def get_count(db_path, isolation_level, name):
    conn = _connect(db_path, isolation_level)
    c = conn.cursor()
    c.execute('''\
    SELECT count FROM test_table
    WHERE name = ?
    ''', (name,))
    (count,) = c.fetchone()
    conn.commit()
    conn.close()
    return count


def increment(db_path, isolation_level, name, sleep_sec=0):
    conn = _connect(db_path, isolation_level)
    c = conn.cursor()
    if isolation_level == 'DEFERRED':
        c.execute('BEGIN DEFERRED')
    elif isolation_level == 'IMMEDIATE':
        c.execute('BEGIN IMMEDIATE')
    else:
        c.execute('BEGIN EXCLUSIVE')
    c.execute('''\
    SELECT count FROM test_table
    WHERE name = ?
    ''', (name,))
    (count,) = c.fetchone()
    if sleep_sec:
        time.sleep(sleep_sec)
    c.execute('''\
    INSERT OR REPLACE INTO test_table
    (name, count)
    VALUES (?, ?)
    ''', (name, count + 1))
    conn.commit()
    conn.close()


def incrementer_process(db_path, isolation_level, name, num,
                        sleep_sec=0):
    for i in range(num):
        increment(db_path, isolation_level, name, sleep_sec=sleep_sec)


def run_threads(db_path, isolation_level, logger):
    name = 'name'
    conn = _connect(db_path, isolation_level)
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
    num_processes = 10
    num_count = 10
    expected_count = num_processes * num_count
    sleep_sec = 0
    processes = []
    for i in range(num_processes):
        process_args = (db_path, isolation_level, name, num_count)
        process_kwargs = {'sleep_sec': sleep_sec}
        logger.debug('Creating process {}'.format(i))
        p = multiprocessing.Process(target=incrementer_process,
                                    args=process_args,
                                    kwargs=process_kwargs)
        p.start()
        processes.append(p)
    for i, p in enumerate(processes):
        logger.debug('Joining process {}'.format(i))
        p.join()
    result = get_count(db_path, isolation_level, name)
    logger.info('result: {}'.format(result))
    if expected_count != result:
        logger.info('Some race condition occured ({} != {})'
                    .format(expected_count, result))


def main():
    parser = ArgumentParser(description=(__doc__),
                            formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('--log', default='INFO',
                        help=('Set log level.'
                              ' NOTSET, DEBUG, INFO, WARN, ERROR, CRITICAL'
                              ' is available'))
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Same as --log DEBUG')
    parser.add_argument('-w', '--warn', action='store_true',
                        help='Same as --log WARN')
    parser.add_argument('-i', '--isolation-level',
                        choices=['n', 'd', 'i', 'e'],
                        default='d')
    args = parser.parse_args()

    if args.isolation_level == 'n':
        isolation_level = None  # Auto-commit mode
    elif args.isolation_level == 'd':
        isolation_level = 'DEFERRED'
    elif args.isolation_level == 'i':
        isolation_level = 'IMMEDIATE'
    else:
        isolation_level = 'EXCLUSIVE'

    logger = getLogger(__name__)
    handler = StreamHandler()
    logger.addHandler(handler)
    if args.debug:
        logger.setLevel(DEBUG)
        handler.setLevel(DEBUG)
    elif args.warn:
        logger.setLevel(WARN)
        handler.setLevel(WARN)
    else:
        if args.log.upper() not in _LOG_LEVELS:
            parser.print_help(file=sys.stderr)
            print('\nInvalid option specified', file=sys.stderr)
            sys.exit(1)
        log_level = _LOG_LEVELS[args.log.upper()]
        logger.setLevel(log_level)
        handler.setLevel(log_level)
    # e.g. '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(Formatter('%(asctime)s %(message)s'))
    logger.info('Start Running')
    logger.info('module_version: {}'.format(sqlite3.version))
    logger.info('sqlite3_version: {}'.format(sqlite3.sqlite_version))
    db_path = os.path.abspath(_DB_PATH)
    run_threads(db_path, isolation_level, logger=logger)
    logger.info('Finished Running')


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
