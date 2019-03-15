"""
This script will load solutionInstanceComponent information.
"""
import logging
from lib import localstore
from lib import my_env
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "solinstcomp"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Solution Instance Components", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    solInstId = row["solutionInstanceId"]
    softInstId = row["softwareInstanceId"]
    solId = row["solutionId"]
    serverId = row["serverId"].lower()
    softId = row["softwareId"]
    validFrom = row["validFrom"]
    if validFrom:
        mode = "FMO"
    else:
        mode = "CMO"
    r.add_solInstComp(solInstId=solInstId, softInstId=softInstId, solId=solId, serverId=serverId, softId=softId,
                      mode=mode)
my_loop.end_loop()
