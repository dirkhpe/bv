"""
This script will convert murcs data and load it into Neo4J.
This is done calling applications in sequence.
"""

# Allow lib to library import path.
import argparse
import os
import logging
import pandas
from lib import my_env
from lib.my_env import run_script

parser = argparse.ArgumentParser(
    description="Batch coupling server to solution"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the file with servers - solutions to link.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
logging.info("Arguments: {a}".format(a=args))
cfg = my_env.init_env("bellavista", __file__)
(fp, filename) = os.path.split(__file__)
script = "server_to_application_create.py"
df = pandas.read_excel(args.filename)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get solution  component node
    hostName = xl.pop("hostName")
    solId = xl.pop("solID")
    params = ["-s", hostName, "-a", str(solId)]
    run_script(fp, script, *params)
