# -*- coding: utf-8 -*-

import os
import configparser
from classes.Registry import Registry
from classes.Database import Database


class CommonUnit(object):
    db = None

    def setup_class(self):
        CURPATH = os.path.dirname(__file__) + "/"

        config = configparser.ConfigParser()
        config.read(CURPATH + 'config.ini')
        Registry().set('config', config)

        db = Database(
            config['main']['mysql_host'],
            config['main']['mysql_user'],
            config['main']['mysql_pass'],
            config['main']['mysql_dbname'],
        )
        Registry().set('db', db)

        self.db = Registry().get('db')  # type: Database

    def _clean_db(self):
        self.db.q("TRUNCATE TABLE dicts")
        self.db.q("TRUNCATE TABLE dicts_groups")
        self.db.q("TRUNCATE TABLE hashes")
        self.db.q("TRUNCATE TABLE hashlists")
        self.db.q("TRUNCATE TABLE rules")
        self.db.q("TRUNCATE TABLE tasks")
        self.db.q("TRUNCATE TABLE tasks_groups")
        self.db.q("TRUNCATE TABLE task_works")

    def _add_hashlist(self, id=1, name='test', alg_id=3, have_salts=0, status='ready', common_by_alg=0, parsed=1):
        self.db.insert(
            "hashlists",
            {
                'id': id,
                'name': name,
                'alg_id': alg_id,
                'have_salts': have_salts,
                'delimiter': '',
                'cracked': 0,
                'uncracked': 0,
                'errors': '',
                'parsed': parsed,
                'tmp_path': '',
                'status': status,
                'when_loaded': 0,
                'common_by_alg': common_by_alg,
            }
        )

    def _add_hash(self, hashlist_id=1, hash='', salt='', summ='', password='', cracked=0, id=None):
        self.db.insert(
            "hashes",
            {
                'id': id,
                'hashlist_id': hashlist_id,
                'hash': hash,
                'salt': salt,
                'password': password,
                'cracked': cracked,
                'summ': summ
            }
        )

    def _add_work_task(self, id=1, hashlist_id=1, task_id=1, status='wait', ):
        self.db.insert(
            "task_works",
            {
                'id': id,
                'hashlist_id': hashlist_id,
                'task_id': task_id,
                'status': status
            }
        )