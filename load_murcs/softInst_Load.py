"""
This script will load a software Instance file.
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
                    help='Please provide the software Instance file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

excludedprops = excludedprops
excludedprops.append("hostName")

# Read the file
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("Software Instance", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    softwareInstanceId = xl.pop("softwareInstanceId")
    xl["serverId"] = xl["serverId"].lower()
    payload = dict(
        softwareInstanceId=softwareInstanceId
    )
    for k in xl:
        if pandas.notnull(xl[k]) and k not in excludedprops:
            if k in softInst_prop2dict:
                payload[softInst_prop2dict[k][0]] = {softInst_prop2dict[k][1]: xl[k]}
            else:
                payload[k] = xl[k]
    r.add_softInst(softwareInstanceId, payload)
my_loop.end_loop()
