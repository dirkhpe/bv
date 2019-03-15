"""
This script will load the IP Address information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "ipaddress"
logging.info("Handling table: {t}".format(t=tablename))

# Collect serverId for interfaceId
query = """
    SELECT distinct net.serverId as serverId, ip.serverNetworkInterfaceId as ifaceId
    FROM ipaddress ip
    INNER JOIN netiface net ON ip.serverNetworkInterfaceId = net.networkInterfaceId
"""
res = lcl.get_query(query)
netiface2server = {}
for rec in res:
    netiface2server[rec["ifaceId"]] = rec["serverId"]

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("IP Address Information", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    ipAddress = row.pop("ipAddress")
    interfaceId = row.pop("serverNetworkInterfaceId")
    serverId = netiface2server[interfaceId]
    payload_ip = dict(
        serverNetworkInterfaceId=interfaceId,
        ipAddress=ipAddress
    )
    for k in row:
        if row[k] and k not in excludedprops:
            payload_ip[k] = row[k]
    r.add_serverNetIfaceIp(serverId, interfaceId, ipAddress, payload_ip)
my_loop.end_loop()
