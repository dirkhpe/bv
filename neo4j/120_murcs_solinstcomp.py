import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import neostore
from lib.neostructure import *

ignore = excludedprops + ["solInstId_nr", "softInstId_nr", "serverId", "softId", "solId"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
lcl = localstore.sqliteUtils(cfg)

# Get solution components
solcomp_nodes = ns.get_nodes(lbl_solcomp)
solcomp_d = {}
for node in solcomp_nodes:
    solcomp_d[node["solutionInstanceId"]] = node
instance_nodes = ns.get_nodes(lbl_instance)
instance_d = {}
for node in instance_nodes:
    instance_d[node["softwareInstanceId"]] = node

solinstcomp_recs = lcl.get_table("solinstcomp")
my_loop = my_env.LoopInfo("SolInstComp", 20)
for trow in solinstcomp_recs:
    # Get excel row in dict format
    row = dict(trow)
    # Get solution component node
    solcomp = row.pop("solutionInstanceId")
    solcomp_node = solcomp_d[solcomp]
    inst = row.pop("softwareInstanceId")
    inst_node = instance_d[inst]
    node_params = {}
    # First check for validFrom - is this FMO mode?
    mode = row.pop("validFrom")
    if mode:
        node_params["mode"] = "FMO"
    else:
        node_params["mode"] = "CMO"
    for k in row:
        if k not in ignore:
            if row[k]:
                node_params[k] = row[k]
    solinstcomp_node = ns.create_node(lbl_solinstcomp, **node_params)
    ns.create_relation(from_node=inst_node, rel=instance2solinstcomp, to_node=solinstcomp_node)
    ns.create_relation(from_node=solinstcomp_node, rel=solinstcomp2solcomp, to_node=solcomp_node)
    my_loop.info_loop()
my_loop.end_loop()
