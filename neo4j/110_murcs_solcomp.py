import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import neostore
from lib.neostructure import *

ignore = excludedprops + ["solId_nr"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
lcl = localstore.sqliteUtils(cfg)

# Get solutions
solution_nodes = ns.get_nodes(lbl_solution)
solution_d = {}
for node in solution_nodes:
    solution_d[node["solutionId"]] = node
solcomp_recs = lcl.get_table("solinst")
my_loop = my_env.LoopInfo("SolComp", 20)
for trow in solcomp_recs:
    # Get excel row in dict format
    row = dict(trow)
    # Get solution node
    solId = row.pop("solutionId")
    sol_node = solution_d[str(solId)]
    node_params = {}
    for k in row:
        if k not in ignore:
            if row[k]:
                node_params[k] = row[k]
    solcomp_node = ns.create_node(lbl_solcomp, **node_params)
    ns.create_relation(from_node=solcomp_node, rel=solcomp2solution, to_node=sol_node)
    my_loop.info_loop()
my_loop.end_loop()
