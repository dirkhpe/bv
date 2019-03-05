"""
This script will read the server table and convert it to a Neo4J database.
"""

import logging
from lib import localstore
from lib import my_env
from lib.neostructure import *
from lib import neostore

ign_srv = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "category", "classification",
           "currentApproach", "futureApproach", "hwModel", "managementRegion", "clientId", "osId", "softName",
           "softVersion", "softVendor", "softSubType", "OSDescription", "primaryIP"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
lcl = localstore.sqliteUtils(cfg)
ns = neostore.NeoStore(cfg)

servers = lcl.get_table("server")
parentServer_d = {}
siteId_d = {}
srv_node_d = {}
my_loop = my_env.LoopInfo("Servers", 20)
for trow in servers:
    # Get excel row in dict format
    row = dict(trow)
    # Get server links
    serverType = row.pop("serverType")
    parentServer = row.pop("parentServer")
    if parentServer:
        parentServer_d[row["serverId"]] = parentServer
    siteId = row.pop("siteId")
    if serverType == "PHYSICAL":
        # Remember SiteId only for physical servers.
        if siteId:
            siteId_d[row["serverId"]] = siteId
    # Server link information is handled and removed from row, now handle remaining columns
    node_params = {}
    for k in row:
        if k not in ign_srv:
            if row[k]:
                node_params[k] = row[k]
    srv_node_d[row["serverId"]] = ns.create_node(lbl_server, **node_params)
    my_loop.info_loop()
my_loop.end_loop()

# Link to Parent Server
my_loop = my_env.LoopInfo("Link to Parent", 20)
for k in parentServer_d:
    # There needs to be a node for parent and child at this time
    ns.create_relation(from_node=srv_node_d[parentServer_d[k]], rel=parent2server, to_node=srv_node_d[k])
    my_loop.info_loop()
my_loop.end_loop()

# Link to Site
# Get site nodes
site_nodes = ns.get_nodes(lbl_site)
site_node_d = {}
for node in site_nodes:
    site_node_d[node["siteId"]] = node
# Link server to site
my_loop = my_env.LoopInfo("Link to Site", 20)
for k in siteId_d:
    ns.create_relation(from_node=site_node_d[siteId_d[k]], rel=site2server, to_node=srv_node_d[k])
    my_loop.info_loop()
my_loop.end_loop()
