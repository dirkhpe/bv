"""
This script will restore a Bellavista dump onto a MURCS instance.
"""

# Allow lib to library import path.
import os
import logging
from lib import my_env
from lib.my_env import run_script

scripts = ["site_Load",
           "server_Load",
           "server_Load",   # To link servers with parent servers
           "soft_Load",
           "softInst_Load",
           "solution_Load",
           "solutionInstance_Load",
           "solInstComp_Load",
           "solutionToSolution_Load",
           "netiface_Load",
           "ipaddress_Load",
           "person_Load",
           "contactServer_Load",
           "contactSolution_Load",
           "serverProperty_Load",
           "solutionProperty_Load",
           "solutionInstanceProperty_Load"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
(fp, filename) = os.path.split(__file__)
for script in scripts:
    logging.info("Run script: {s}".format(s=script))
    run_script(fp, script + ".py")
