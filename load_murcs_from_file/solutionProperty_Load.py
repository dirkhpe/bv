"""
This script will load a solution Property file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib.murcs import *
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Solution Property file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the solution property file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename, converters={'solutionId': str})
my_loop = my_env.LoopInfo("Solution Properties", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    solutionId = xl.pop("solutionId")
    payload = dict(
        solutionId=solutionId
    )
    for k in xl:
        if pandas.notnull(xl[k]) and k not in excludedprops:
            if k in fixedprops:
                payload[k] = fixedprops[k]
            elif k in srv_prop2dict:
                payload[srv_prop2dict[k][0]] = {srv_prop2dict[k][1]: xl[k]}
            else:
                payload[k] = xl[k]
    r.add_solution_property(solutionId, payload)
my_loop.end_loop()
