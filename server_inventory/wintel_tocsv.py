"""
This script will consolidate all files from a wintel discovery into a csv file per category. There is a file per server
and per type.
The information in each file needs to be converted to a line for the csv file.
The number of columns is variable. Importing into database was not sufficiently successful.
"""

# import csv
import logging
import os
# import sys
from lib import my_env
from lib.localstore import sqliteUtils

# infotypes = ["os"]
infotypes = ["computersystem", "cpu", "diskdrive", "environment", "job", "logicaldisk", "nicconfig", "os", "pagefile",
             "partition", "printer", "process", "product", "quotasetting", "service", "share", "sysaccount",
             "useraccount"]
stats = {}


cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
db = cfg['Main']['db']
ds = sqliteUtils(cfg)

windir = cfg['Main']['windir']
for infotype in infotypes:
    file_ext = "_{t}.csv".format(t=infotype)
    csv_file_name = "all_{t}.csv".format(t=infotype)
    csv_file = os.path.join(cfg['Main']['logdir'], csv_file_name)
    nr_fields = -1
    stats[infotype] = dict(
        ok=0,
        no_info=0,
        empty_file=0
    )
    # ds.create_table(table_name, row)
    filelist = [file for file in os.listdir(windir) if file[len(file)-len(file_ext):] == file_ext]
    my_loop = my_env.LoopInfo(infotype, 20)
    with open(csv_file, 'w', encoding='utf-8') as csv_hdl:
        for file in filelist:
            my_loop.info_loop()
            win_file = os.path.join(windir, file)
            # logging.info("Investigating file {fn} for table {tn}".format(fn=win_file, tn=table_name))
            with open(win_file, 'rb') as win_inv:
                win_reader_utf16 = win_inv.read()
                if len(win_reader_utf16) > 0:
                    win_reader = win_reader_utf16.decode('utf-16')
                    win_lines = win_reader.split('\r\n')
                    if len(win_lines) > 2:
                        if nr_fields < 0:
                            csv_hdl.write(win_lines[1]+"\n")
                            nr_fields = 8
                        for line in win_lines[2:]:
                            line = line.replace(", ", "; ")
                            csv_hdl.write(line+"\n")
                        stats[infotype]["ok"] += 1
                    else:
                        stats[infotype]["no_info"] += 1
                else:
                    stats[infotype]["empty_file"] += 1
        my_loop.end_loop()

stat_fn = os.path.join(cfg['Main']['logdir'], "statistics.csv")
stat_fh = open(stat_fn, 'w')
stat_fh.write(";OK;No Info;Empty File\n")
for infotype in stats:
    stat_fh.write("{it};{ok};{ni};{ef}\n".format(it=infotype, ok=stats[infotype]["ok"], ni=stats[infotype]["no_info"],
                                                 ef=stats[infotype]["empty_file"]))
stat_fh.close()
