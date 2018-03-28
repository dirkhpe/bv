"""
This script will convert murcs data and load it into Neo4J.
This is done calling applications in sequence.
"""

# Allow lib to library import path.
import os
import logging
from lib import my_env
from lib.my_env import run_script

scripts = [
    "person",
    "server",
    "server_ip",
    "server_person",
    "server_property",
    "server_soft",
    "site",
    "soft",
    "softinst_property",
    "solution",
    "solution_component",
    "solution_component_instance",
    "solution_component_property",
    "solution_person",
    "solution_property",
    "solution_to_solution"
    ]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
(fp, filename) = os.path.split(__file__)
for script in scripts:
    logging.info("Run script: {s}.py".format(s=script))
    run_script(fp, "{s}.py".format(s=script))
