#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is part of HashBruteStation software
Docs EN: http://hack4sec.pro/wiki/index.php/Hash_Brute_Station_en
Docs RU: http://hack4sec.pro/wiki/index.php/Hash_Brute_Station
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)

 Main cron of HBS
"""

import time
import os
import subprocess

import configparser

from classes.Factory import Factory
from classes.Registry import Registry
from classes.WorkerThread import WorkerThread
from classes.HashlistsLoaderThread import HashlistsLoaderThread
from classes.ResultParseThread import ResultParseThread
from classes.HashlistsByAlgLoaderThread import HashlistsByAlgLoaderThread
from classes.FinderInsideProThread import FinderInsideProThread
from classes.Logger import Logger

config = configparser.ConfigParser()
config.read(os.getcwd() + '/' + 'config.ini')
Registry().set('config', config)

db = Factory().new_db_connect()

if not os.path.exists(config['main']['tmp_dir']):
    print "ERROR: Tmp path {0} is not exists!".format(config['main']['tmp_dir'])
    exit(0)

if not os.access(config['main']['tmp_dir'], os.W_OK):
    print "ERROR: Tmp path {0} is not writable!".format(config['main']['tmp_dir'])
    exit(0)

if not os.path.exists(config['main']['outs_path']):
    print "ERROR: Outs path {0} is not exists!".format(config['main']['outs_path'])
    exit(0)

if not os.access(config['main']['outs_path'], os.W_OK):
    print "ERROR: Outs path {0} is not writable!".format(config['main']['outs_path'])
    exit(0)

if not os.path.exists(config['main']['dicts_path']):
    print "ERROR: Dicts path {0} is not exists!".format(config['main']['dicts_path'])
    exit(0)

if not os.access(config['main']['dicts_path'], os.W_OK):
    print "ERROR: Dicts path {0} is not writable!".format(config['main']['dicts_path'])
    exit(0)

if not os.path.exists(config['main']['path_to_hc']):
    print "ERROR: HC path {0} is not exists!".format(config['main']['path_to_hc'])
    exit(0)

if not os.path.exists("{0}/{1}".format(config['main']['path_to_hc'], config['main']['hc_bin'])):
    print "ERROR: HC bin {0}/{1} is not exists!".format(config['main']['path_to_hc'], config['main']['hc_bin'])
    exit(0)

version_output = subprocess.check_output(
    "{0}/{1} --version".format(config['main']['path_to_hc'], config['main']['hc_bin']), shell=True)
if version_output[0] != '2':
    print "ERROR: HBS support only HashCat v2, but you have {0} ({1})".format(version_output[0], version_output)
    exit(0)

Registry().set('db', db)

#logger_db = Factory().new_db_connect()
#Registry().set('logger_db', logger_db)

logger = Logger()
Registry().set('logger', logger)

Registry().get('logger').log("main", "Started")

hashlists_loader_thrd = HashlistsLoaderThread()
hashlists_loader_thrd.start()

result_parse_thrd = ResultParseThread()
result_parse_thrd.start()

hashlists_by_alg_loader_thrd = HashlistsByAlgLoaderThread()
hashlists_by_alg_loader_thrd.start()

if len(config['main']['finder_key']):
    finder_insidepro_thrd = FinderInsideProThread()
    finder_insidepro_thrd.start()
else:
    Registry().get('logger').log('main', 'FinderInsidePro key not found, service will not start')

work_thrd = None
while True:
    next_work_task = db.fetch_row(
        "SELECT tw.* FROM task_works tw, hashlists hl "
        "WHERE tw.hashlist_id = hl.id AND hl.parsed AND tw.status='wait' "
        "AND hl.alg_id NOT IN( "
        " SELECT hl.alg_id FROM `task_works` tw, hashlists hl, algs a "
        " WHERE tw.hashlist_id = hl.id AND hl.alg_id = a.id AND tw.status IN('waitoutparse', 'outparsing') "
        ") "
        "ORDER BY tw.priority DESC LIMIT 1"
    )
    if next_work_task:
        work_thrd = WorkerThread(next_work_task)
        work_thrd.start()

        while not work_thrd.done:
            time.sleep(3)

        del work_thrd
        work_thrd = None
    else:
        pass

    time.sleep(5)
