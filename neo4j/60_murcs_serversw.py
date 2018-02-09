import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
instlbl = "Instance"
serverlbl = "Server"
softVersionlbl = "softVersion"
# Relations
server2inst = "serverInst"
inst2version = "isVersion"

ignore = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "clientId"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
serversw_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["serversw"])
df = pandas.read_excel(serversw_file)
# Get Server Nodes
server_nodes = ns.get_nodes(serverlbl)
server_d = {}
for node in server_nodes:
    server_d[node["serverId"]] = node
# Get software Nodes
soft_nodes = ns.get_nodes(softVersionlbl)
soft_d = {}
for node in soft_nodes:
    soft_d[node["softId"]] = node

# Now handle all lines
my_loop = my_env.LoopInfo("Server to Soft", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    serverId = xl.pop("serverId")
    server_node = server_d[serverId]
    softId = xl.pop("softId")
    soft_node = soft_d[softId]
    node_params = {}
    for k in xl:
        if k not in ignore:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    inst_node = ns.create_node(instlbl, **node_params)
    ns.create_relation(from_node=server_node, rel=server2inst, to_node=inst_node)
    ns.create_relation(from_node=inst_node, rel=inst2version, to_node=soft_node)
my_loop.end_loop()
