"""
This script will load server Property information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "serverproperty"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Server Properties", 20)
for trow in records:
    my_loop.info_loop()
    # Get excel row in dict format
    row = dict(trow)
    serverId = row.pop("serverId").lower()
    payload = dict(
        serverId=serverId
    )
    for k in row:
        if row[k] and k not in excludedprops:
            if k in fixedprops:
                payload[k] = fixedprops[k]
            elif k in srv_prop2dict:
                payload[srv_prop2dict[k][0]] = {srv_prop2dict[k][1]: row[k]}
            else:
                payload[k] = row[k]
    r.add_server_property(serverId, payload)
my_loop.end_loop()
