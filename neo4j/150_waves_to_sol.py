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
# First handle wave information
df = pandas.read_excel(appsgroup_file, sheet_name="waves")
wave_d = {}
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    node_params = dict(
        name=xl.pop("Name"),
        wave=xl.pop("Wave")
    )
    for k in xl:
        if pandas.notnull(xl[k]):
            if isinstance(xl[k], pandas._libs.Timestamp):
                node_params[k] = xl[k].strftime("%Y-%m-%d")
            else:
                node_params[k] = xl[k]
    wave_d[node_params["wave"]] = ns.create_node(wavelbl, **node_params)

# Then handle solution per wave
df = pandas.read_excel(appsgroup_file, sheet_name="full list")
my_loop = my_env.LoopInfo("AppsGroup", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution component node
    # Only handle file if Migration group is available.
    miggroup = xl["Wave"]
    if pandas.isnull(miggroup):
        miggroup = "NA"
    try:
        wave_node = wave_d[miggroup]
    except KeyError:
        node_params = dict(
            wave=miggroup
        )
        wave_d[miggroup] = ns.create_node(wavelbl, **node_params)
        wave_node = wave_d[miggroup]
    solId = xl["Unique ID"]
    if pandas.notnull(solId):
        try:
            sol_node = solution_d[str(int(solId))]
        except KeyError:
            logging.error("SolId {solId} not defined!".format(solId=solId))
        else:
            ns.create_relation(from_node=sol_node, rel=solution2wave, to_node=wave_node)
    my_loop.info_loop()
my_loop.end_loop()
