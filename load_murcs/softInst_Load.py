"""
This script will load software Instance information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "softinst"
logging.info("Handling table: {t}".format(t=tablename))

excludedprops.append("hostName")

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Software Instance", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    softwareInstanceId = row.pop("softwareInstanceId")
    row["serverId"] = row["serverId"].lower()
    payload = dict(
        softwareInstanceId=softwareInstanceId
    )
    for k in row:
        if row[k] and k not in excludedprops:
            if k in softInst_prop2dict:
                payload[softInst_prop2dict[k][0]] = {softInst_prop2dict[k][1]: row[k]}
            else:
                payload[k] = row[k]
    r.add_softInst(softwareInstanceId, payload)
my_loop.end_loop()
