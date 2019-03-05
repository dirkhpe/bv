import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import neostore
from lib.neostructure import *

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
lcl = localstore.sqliteUtils(cfg)

# Then handle all software Instances
# Get Server Nodes
server_nodes = ns.get_nodes(lbl_server)
server_d = {}
for node in server_nodes:
    server_d[node["serverId"]] = node
# Get software Nodes
soft_nodes = ns.get_nodes(lbl_softVersion)
soft_d = {}
for node in soft_nodes:
    soft_d[node["softwareId"]] = node

# Now handle software instances
serversw_recs = lcl.get_table("softinst")
my_loop = my_env.LoopInfo("Server to Soft", 20)
for trow in serversw_recs:
    my_loop.info_loop()
    # Get excel row in dict format
    xl = dict(trow)
    serverId = xl.pop("serverId")
    server_node = server_d[serverId]
    softId = xl.pop("softwareId")
    soft_node = soft_d[softId]
    node_params = {}
    for k in xl:
        if k not in excludedprops:
            if xl[k]:
                node_params[k] = xl[k]
    inst_node = ns.create_node(lbl_instance, **node_params)
    ns.create_relation(from_node=server_node, rel=server2instance, to_node=inst_node)
    ns.create_relation(from_node=inst_node, rel=instance2softVersion, to_node=soft_node)
my_loop.end_loop()
