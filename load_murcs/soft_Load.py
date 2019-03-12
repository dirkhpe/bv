"""
This script will load software information.
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
    payload = dict(
        softwareId=softwareId
    )
    for k in row:
        if row[k] and k not in excludedprops:
            if k in fixedprops:
                payload[k] = fixedprops[k]
            else:
                payload[k] = row[k]
    r.add_soft(softwareId, payload)
my_loop.end_loop()
