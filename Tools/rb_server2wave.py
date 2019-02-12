"""
This script will collect initial version of the runbook.

"""

import logging
import os
import pandas
from lib import my_env
from lib import neostore

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
query = """
    MATCH (wave:Wave)<-[:inWave]-(sol),
        (sol)<-[:fromSolution]-(solComp),
        (solComp)<-[:toComponent]-(instComp),
        (instComp)<-[:toInstComp]-(inst),
        (inst)<-[:serverInst]-(server:Server)
    RETURN wave.name as wave, sol.solName as solution, inst.instSubType as Type, server.hostName as host
"""
res = ns.get_query_df(query)
ofp = cfg["MurcsDump"]["dump_dir"]
of = os.path.join(ofp, "rb.xlsx")
res.to_excel(of)