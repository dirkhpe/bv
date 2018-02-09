import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
solutionlbl = "Solution"
# Relations
sol2sol = "sol2sol"

ignore = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "clientid", "solId_nr"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
# Get solutions
solution_nodes = ns.get_nodes(solutionlbl)
solution_d = {}
for node in solution_nodes:
    solution_d[node["solId"]] = node
sol2sol_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["sol2sol"])
df = pandas.read_excel(sol2sol_file)
my_loop = my_env.LoopInfo("Sol2sol", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution node
    fromSolId = xl.pop("fromSolId")
    from_sol_node = solution_d[str(fromSolId)]
    toSolId = xl.pop("toSolId")
    to_sol_node = solution_d[str(toSolId)]
    dir = xl.pop("conDirection")
    if dir != "T2S":
        ns.create_relation(from_node=from_sol_node, rel=sol2sol, to_node=to_sol_node)
    if dir != "S2T":
        ns.create_relation(from_node=to_sol_node, rel=sol2sol, to_node=from_sol_node)
    my_loop.info_loop()
my_loop.end_loop()
