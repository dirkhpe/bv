"""
This script will load the network interface information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "netiface"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Network Interface Information", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    serverId = row.pop("serverId").lower()
    interfaceId = row.pop("networkInterfaceId")
    payload_if = dict(
        networkInterfaceId=interfaceId,
        serverId=serverId
    )
    for k in row:
        if row[k] and k not in excludedprops:
            payload_if[k] = row[k]
    r.add_serverNetIface(serverId, interfaceId, payload_if)
my_loop.end_loop()
