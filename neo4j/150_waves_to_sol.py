import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
solutionlbl = "Solution"
wavelbl = "Wave"
# Relations
solution2wave = "inWave"

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
# Get solution components
solution_nodes = ns.get_nodes(solutionlbl)
solution_d = {}
for node in solution_nodes:
    solution_d[node["solId"]] = node
appsgroup_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["appsgroup"])
df = pandas.read_excel(appsgroup_file, sheet_name="apps")
wave_d = {}
my_loop = my_env.LoopInfo("AppsGroup", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution component node
    # Only handle file if Migration group is available.
    miggroup = xl["Migration Group"]
    if pandas.notnull(miggroup) and (miggroup != 0):
        try:
            wave_node = wave_d[miggroup]
        except KeyError:
            node_params = dict(
                name=miggroup,
                order=xl["Wave order"]
            )
            wave_d[miggroup] = ns.create_node(wavelbl, **node_params)
            wave_node = wave_d[miggroup]
        solId = xl["UniqueId"]
        try:
            sol_node = solution_d[str(solId)]
        except KeyError:
            logging.error("SolId {solId} not defined!".format(solId=solId))
        else:
            ns.create_relation(from_node=sol_node, rel=solution2wave, to_node=wave_node)
    my_loop.info_loop()
my_loop.end_loop()
