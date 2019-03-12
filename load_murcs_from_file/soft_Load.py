"""
This script will load a software file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib.murcs import *
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Server file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the software file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("Software", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    softwareId = xl.pop("softwareId")
    payload = dict(
        softwareId=softwareId
    )
    for k in xl:
        if pandas.notnull(xl[k]) and k not in excludedprops:
            if k in fixedprops:
                payload[k] = fixedprops[k]
            else:
                payload[k] = xl[k]
    r.add_soft(softwareId, payload)
my_loop.end_loop()
