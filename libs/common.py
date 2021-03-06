"""
This is part of HashBruteStation software
Docs EN: http://hack4sec.pro/wiki/index.php/Hash_Brute_Station_en
Docs RU: http://hack4sec.pro/wiki/index.php/Hash_Brute_Station
License: MIT
Copyright (c) Anton Kuzmin <http://anton-kuzmin.ru> (ru) <http://anton-kuzmin.pro> (en)
"""
import sys
import time
import hashlib
import random


def _d(source, _str, new_line=True, prefix=True):
    """ Debug output (with time) """
    if prefix:
        print "[{0}][{1}] {2}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            source.upper(),
            _str.strip()
        ),
    else:
        print _str.strip(),
    if new_line:
        print '\n',
    sys.stdout.flush()


def file_lines_count(path):
    count = 0
    fh = open(path)
    for _l in fh:
        count += 1
    fh.close()
    return count

def gen_random_md5():
    return md5(str(time.time()) + str(random.randint(0, 9999999)))

def md5(string):
    m = hashlib.md5()
    m.update(string.encode('UTF-8'))
    return m.hexdigest()


def file_put_contents(path_to_file, content, add=False):
    """ Function put content to a file (analog of php file_put_contents()) """
    fh = open(path_to_file, 'a' if add else 'w')
    fh.write(content)
    fh.close()


def file_get_contents(path_to_file):
    """ Function get content of file (analog of php file_get_contents()) """
    fh = open(path_to_file, 'r')
    content = fh.read()
    fh.close()
    return content

def update_hashlist_counts(db, id):
    cracked = db.fetch_one("SELECT COUNT(id) FROM hashes WHERE hashlist_id = {0} AND cracked".format(id))
    uncracked = db.fetch_one("SELECT COUNT(id) FROM hashes WHERE hashlist_id = {0} AND !cracked".format(id))
    db.update("hashlists", {'cracked': cracked, 'uncracked': uncracked}, "id = {0}".format(id))

