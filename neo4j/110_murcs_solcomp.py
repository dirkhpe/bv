import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
solutionlbl = "Solution"
solcomplbl = "SolComp"
# Relations
solcomp2sol = "fromSolution"

ignore = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "clientid", "environment", "solId_nr"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
# Get solutions
solution_nodes = ns.get_nodes(solutionlbl)
solution_d = {}
for node in solution_nodes:
    solution_d[node["solId"]] = node
solcomp_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["solcomp"])
df = pandas.read_excel(solcomp_file)
my_loop = my_env.LoopInfo("SolComp", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution node
    solId = xl.pop("solId")
    sol_node = solution_d[str(solId)]
    node_params = {}
    for k in xl:
        if k not in ignore:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    solcomp_node = ns.create_node(solcomplbl, **node_params)
    ns.create_relation(from_node=solcomp_node, rel=solcomp2sol, to_node=sol_node)
    my_loop.info_loop()
my_loop.end_loop()
