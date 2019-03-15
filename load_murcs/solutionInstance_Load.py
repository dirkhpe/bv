"""
This script will load solutionInstance information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "solution"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table("solinst")
my_loop = my_env.LoopInfo("Solution Instances", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    solutionInstanceId = row.pop("solutionInstanceId")
    solutionId = row["solutionId"]
    payload = dict(
        solutionInstanceId=solutionInstanceId
    )
    for k in row:
        if row[k] and k not in excludedprops:
            if k in fixedprops:
                payload[k] = fixedprops[k]
            elif k in solInst_prop2dict:
                payload[solInst_prop2dict[k][0]] = {solInst_prop2dict[k][1]: row[k]}
            else:
                payload[k] = row[k]
    r.add_solInst(solutionId, solutionInstanceId, payload)
my_loop.end_loop()
