import logging
import os
import pandas
from lib import localstore
from lib import my_env
from lib import neostore
from lib.neostructure import *

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
lcl = localstore.sqliteUtils(cfg)

# Get solution components
solution_nodes = ns.get_nodes(lbl_solution)
solution_d = {}
for node in solution_nodes:
    solution_d[node["solutionId"]] = node

appsgroup_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["appsgroup"])
wave_d = {}

# Handle solution per wave
df = pandas.read_excel(appsgroup_file, sheet_name="applications")
my_loop = my_env.LoopInfo("AppsGroup", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution component node
    # Only handle file if Migration group is available.
    miggroup = xl["WAVE-GROUP"]
    if pandas.isnull(miggroup):
        miggroup = "NA"
    try:
        wave_node = wave_d[miggroup]
    except KeyError:
        node_params = dict(
            wave=miggroup
        )
        wave_d[miggroup] = ns.create_node(lbl_wave, **node_params)
        wave_node = wave_d[miggroup]
    solId = xl["UniqueId"]
    if pandas.notnull(solId):
        try:
            sol_node = solution_d[str(int(solId))]
        except KeyError:
            logging.error("SolId {solId} not defined!".format(solId=solId))
        else:
            ns.create_relation(from_node=sol_node, rel=solution2wave, to_node=wave_node)
    my_loop.info_loop()
my_loop.end_loop()
