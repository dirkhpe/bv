"""
This script will load solution to solution information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "soltosol"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Solution Instances", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    solToSolId = row.pop("solutionToSolutionId")
    fromSolId = row.pop("fromSolutionId")
    toSolId = row.pop("toSolutionId")
    payload = dict(
        solutionToSolutionId=solToSolId
    )
    for k in row:
        if row[k] and k not in excludedprops:
            payload[k] = row[k]
    r.add_solToSol(solToSolId, fromSolId, toSolId, payload)
my_loop.end_loop()
