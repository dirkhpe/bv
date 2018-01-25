"""
This script will read the file murcs_servers and convert it to a Neo4J database.
"""

import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
serverlbl = "Server"
sitelbl = "Site"
iplbl = "IP"
# Relations
server2ip = "hasIP"
server2parent = "hasParent"
server2site = "inSite"

ign_srv = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "category", "classification",
           "currentApproach", "futureApproach", "hwModel", "managementRegion", "clientId", "osId", "softName",
           "softVersion", "softVendor", "softSubType", "OSDescription", "primaryIP"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
servers_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["servers"])
df = pandas.read_excel(servers_file)
parentServer_d = {}
siteId_d = {}
srv_node_d = {}
my_loop = my_env.LoopInfo("Servers", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get server links
    serverType = xl.pop("serverType")
    parentServer = xl.pop("parentServer")
    if pandas.notnull(parentServer):
        parentServer_d[xl["serverId"]] = parentServer
    siteId = xl.pop("siteId")
    if pandas.notnull(siteId):
        siteId_d[xl["serverId"]] = siteId
    # Server link information is handled and removed from row, now handle remaining columns
    node_params = {}
    for k in xl:
        if k not in ign_srv:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    srv_node_d[xl["serverId"]] = ns.create_node(serverlbl, **node_params)
    my_loop.info_loop()
my_loop.end_loop()

"""
# Link to IP Addresses
ip_node_d = {}
my_loop = my_env.LoopInfo("Link to IP", 20)
for k in primaryIP_d:
    try:
        ip_node = ip_node_d[primaryIP_d[k]]
    except KeyError:
        node_params = dict(
            ip=primaryIP_d[k],
            type='primaryIP'
        )
        ip_node_d[primaryIP_d[k]] = ns.create_node(iplbl, **node_params)
        ip_node = ip_node_d[primaryIP_d[k]]
    ns.create_relation(from_node=srv_node_d[k], rel=server2ip, to_node=ip_node)
    my_loop.info_loop()
my_loop.end_loop()

# Link to Parent Server
my_loop = my_env.LoopInfo("Link to Parent", 20)
for k in parentServer_d:
    # There needs to be a node for parent and child at this time
    ns.create_relation(from_node=srv_node_d[k], rel=server2parent, to_node=srv_node_d[parentServer_d[k]])
    my_loop.info_loop()
my_loop.end_loop()
"""

# Link to Site
# Get site nodes
site_nodes = ns.get_nodes(sitelbl)
site_node_d = {}
for node in site_nodes:
    site_node_d[node["siteId"]] = node
# Link server to site
my_loop = my_env.LoopInfo("Link to Site", 20)
for k in siteId_d:
    ns.create_relation(from_node=srv_node_d[k], rel=server2site, to_node=site_node_d[siteId_d[k]])
    my_loop.info_loop()
my_loop.end_loop()