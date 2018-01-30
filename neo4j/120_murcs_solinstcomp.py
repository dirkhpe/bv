import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
instancelbl = "Instance"
solutionlbl = "Solution"
solcomplbl = "SolComp"
solInstComplbl = "SolInstComp"
# Relations
solinstcomp2comp = "toComponent"
inst2solinstcomp = "toInstComp"

ignore = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "clientid", "solInstId_nr", "softInstId_nr",
          "serverId", "softId", "solId"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
# Get solution components
solcomp_nodes = ns.get_nodes(solcomplbl)
solcomp_d = {}
for node in solcomp_nodes:
    solcomp_d[node["solInstId"]] = node
instance_nodes = ns.get_nodes(instancelbl)
instance_d = {}
for node in instance_nodes:
    instance_d[node["instId"]] = node
solinstcomp_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["solinstcomp"])
df = pandas.read_excel(solinstcomp_file)
my_loop = my_env.LoopInfo("SolInstComp", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution component node
    solcomp = xl.pop("solInstId")
    solcomp_node = solcomp_d[solcomp]
    inst = xl.pop("softInstId")
    inst_node = instance_d[inst]
    node_params = {}
    for k in xl:
        if k not in ignore:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    solinstcomp_node = ns.create_node(solInstComplbl, **node_params)
    ns.create_relation(from_node=inst_node, rel=inst2solinstcomp, to_node=solinstcomp_node)
    ns.create_relation(from_node=solinstcomp_node, rel=solinstcomp2comp, to_node=solcomp_node)
    my_loop.info_loop()
my_loop.end_loop()
