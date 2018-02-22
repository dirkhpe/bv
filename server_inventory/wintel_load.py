"""
This script will load all files from a wintel discovery into a mysql database. Each file be converted in a table.
"""

import csv
import logging
import os
import sys
from lib import my_env
from lib.localstore import sqliteUtils


def get_tablename(filename):
    """
    This method will convert a filename to a tablename. Filenames are format 'all-*'. Tablename is in format 'w
    intel-'.

    :param filename:

    :return:
    """
    basename, _ = os.path.basename(filename).split(".")
    return basename.replace("all-", "wintel_")


cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
db = cfg['Main']['db']
ds = sqliteUtils(cfg)

windir = cfg['Main']['windir']
filelist = [file for file in os.listdir(windir) if file[0:len("all-")] == "all-"]
for file in filelist:
    win_file = os.path.join(windir, file)
    table_name = get_tablename(win_file)
    logging.info("Converting file {fn} to table {tn}".format(fn=win_file, tn=table_name))
    with open(win_file, newline='') as win_inv:
        # delimiter defaults to , - quotechar defaults to "
        win_reader = csv.DictReader(win_inv)
        loop = my_env.LoopInfo(table_name, 100)
        create_table_flag = True
        more_records = True
        while True:
            try:
                row = next(win_reader)
            except StopIteration:
                break
            except:
                e = sys.exc_info()[1]
                ec = sys.exc_info()[0]
                log_msg = "Processing table %s, Error Class: %s, Message: %s"
                logging.critical(log_msg, table_name, ec, e)
                break
            if create_table_flag:
                    ds.create_table(table_name, row)
                    create_table_flag = False
            if row['Node'] != "Node":
                ds.insert_row(table_name, row)
                loop.info_loop()
        loop.end_loop()
