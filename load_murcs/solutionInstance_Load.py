"""
This script will load a solutionInstance file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Solution Instance file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the solution Instance file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename, converters={'solutionId': str})
my_loop = my_env.LoopInfo("Solution Instances", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    solutionInstanceId = xl.pop("solutionInstanceId")
    solutionId = xl["solutionId"]
    payload = dict(
        solutionInstanceId=solutionInstanceId
    )
    for k in xl:
        if pandas.notnull(xl[k]) and k not in my_env.excludedprops:
            if k in my_env.fixedprops:
                payload[k] = my_env.fixedprops[k]
            elif k in my_env.solInst_prop2dict:
                payload[my_env.solInst_prop2dict[k][0]] = {my_env.solInst_prop2dict[k][1]: xl[k]}
            else:
                payload[k] = xl[k]
    r.add_solInst(solutionId, solutionInstanceId, payload)
my_loop.end_loop()
