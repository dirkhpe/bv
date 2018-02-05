import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
solcomplbl = "SolComp"
sapsidlbl = "SapSid"
# Relations
solcomp2sap = "inSid"

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
# Get solution Components
solcomp_nodes = ns.get_nodes(solcomplbl)
solcomp_d = {}
for node in solcomp_nodes:
    solcomp_d[node["solInstId"]] = node
solcompprops_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["solcompprops"])
df = pandas.read_excel(solcompprops_file)
my_loop = my_env.LoopInfo("SolCompProps", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution  component node
    solInstId = xl.pop("solInstId")
    solcomp_node = solcomp_d[solInstId]
    node_params = dict(
        name=xl.pop('propertyValue')
    )
    sap_node = ns.create_node(sapsidlbl, **node_params)
    ns.create_relation(from_node=solcomp_node, rel=solcomp2sap, to_node=sap_node)
    my_loop.info_loop()
my_loop.end_loop()
