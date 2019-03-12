"""
This script will load server information.

Servers need to be loaded before they can be used as a Parent Server.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "server"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Servers", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    serverId = row.pop("serverId").lower()
    payload = dict(
        serverId=serverId
    )
    for k in row:
        if row[k] and k not in srv_excluded:
            if k in fixedprops:
                payload[k] = fixedprops[k]
            elif k in srv_prop2dict:
                payload[srv_prop2dict[k][0]] = {srv_prop2dict[k][1]: row[k]}
            else:
                payload[k] = row[k]
    r.add_server(serverId, payload)
my_loop.end_loop()
