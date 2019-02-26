"""
This script will load a software file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Solution file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the solution file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("Solution", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    solutionId = xl.pop("solutionId")
    payload = dict(
        solutionId=solutionId
    )
    for k in xl:
        if pandas.notnull(xl[k]) and k not in my_env.excludedprops:
            if k in my_env.fixedprops:
                payload[k] = my_env.fixedprops[k]
            else:
                payload[k] = xl[k]
    r.add_sol(solutionId, payload)
my_loop.end_loop()
