import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
solutionlbl = "Solution"
# Relations

ignore = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "clientid", "watchSol", "longDescription",
          "description", "assessmentComplete"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
solutions_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["solutions"])
df = pandas.read_excel(solutions_file)
my_loop = my_env.LoopInfo("Solutions", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    node_params = {}
    for k in xl:
        if k not in ignore:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    ns.create_node(solutionlbl, **node_params)
    my_loop.info_loop()
my_loop.end_loop()
