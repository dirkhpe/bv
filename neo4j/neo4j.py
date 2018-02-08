"""
This script will convert murcs data and load it into Neo4J.
This is done calling applications in sequence.
"""

# Allow lib to library import path.
import os
import logging
from lib import my_env
from lib.my_env import run_script

scripts = ["rebuild_neo4j.py",
           "10_murcs_sites.py",
           "20_murcs_servers.py",
           "50_murcs_soft.py",
           "60_murcs_serversw.py",
           "100_murcs_solutions.py",
           "110_murcs_solcomp.py",
           "120_murcs_solinstcomp.py",
           "130_murcs_solinst.py",
           "150_waves_to_sol.py"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
(fp, filename) = os.path.split(__file__)
for script in scripts:
    logging.info("Run script: {s}".format(s=script))
    run_script(fp, script)
