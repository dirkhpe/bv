"""
This script will remove software information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "software"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Software", 20)
for trow in records:
    my_loop.info_loop()
    # Get excel row in dict format
    row = dict(trow)
    softwareId = row.pop("softwareId")
    r.remove_software(softwareId)
my_loop.end_loop()
