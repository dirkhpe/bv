import logging
from lib import localstore
from lib import my_env
from lib import neostore
from lib.neostructure import *

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
lcl = localstore.sqliteUtils(cfg)

# Get solution Components
solcomp_nodes = ns.get_nodes(lbl_solcomp)
solcomp_d = {}
sap_d = {}
for node in solcomp_nodes:
    solcomp_d[node["solutionInstanceId"]] = node

solcompprops_recs = lcl.get_table("solinstproperty")
my_loop = my_env.LoopInfo("SolCompProps", 20)
for trow in solcompprops_recs:
    # Get excel row in dict format
    xl = dict(trow)
    # Get solution  component node
    solInstId = xl.pop("solutionInstanceId")
    solcomp_node = solcomp_d[solInstId]
    sid = xl.pop('propertyValue')
    node_params = dict(
        name=sid
    )
    try:
        sap_node = sap_d[sid]
    except KeyError:
        sap_d[sid] = ns.create_node(lbl_sapsid, **node_params)
        sap_node = sap_d[sid]
    ns.create_relation(from_node=solcomp_node, rel=solcomp2sap, to_node=sap_node)
    my_loop.info_loop()
my_loop.end_loop()
