import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import neostore
from lib.neostructure import *

ignore = excludedprops + ["longDescription", "description", "assessmentComplete"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
lcl = localstore.sqliteUtils(cfg)

solutions_recs = lcl.get_table("solution")
my_loop = my_env.LoopInfo("Solutions", 20)
for trow in solutions_recs:
    # Get excel row in dict format
    row = dict(trow)
    node_params = {}
    for k in row:
        if k not in ignore:
            if row[k]:
                node_params[k] = row[k]
    ns.create_node(lbl_solution, **node_params)
    my_loop.info_loop()
my_loop.end_loop()
