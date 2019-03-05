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

sol2sol_recs = lcl.get_table("soltosol")
my_loop = my_env.LoopInfo("Sol2sol", 20)
for trow in sol2sol_recs:
    # Get excel row in dict format
    xl = dict(trow)
    # Get solution node
    fromSolId = xl.pop("fromSolutionId")
    from_sol_node = solution_d[str(fromSolId)]
    toSolId = xl.pop("toSolutionId")
    to_sol_node = solution_d[str(toSolId)]
    direction = xl.pop("connectionDirection")
    if direction != "T2S":
        ns.create_relation(from_node=from_sol_node, rel=solution2solution, to_node=to_sol_node)
    if direction != "S2T":
        ns.create_relation(from_node=to_sol_node, rel=solution2solution, to_node=from_sol_node)
    my_loop.info_loop()
my_loop.end_loop()
