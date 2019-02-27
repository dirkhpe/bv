"""
This script will load a solutionInstanceComponent file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Solution Instance Component file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the solution Instance Component file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename, converters={'solId': str})
my_loop = my_env.LoopInfo("Solution Instance Components", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    solInstId = xl["solInstId"]
    softInstId = xl["softInstId"]
    solId = xl["solId"]
    serverId = xl["serverId"].lower()
    softId = xl["softId"]
    validFrom = xl["validFrom"]
    if pandas.isnull(validFrom):
        mode = "CMO"
    else:
        mode = "FMO"
    r.add_solInstComp(solInstId=solInstId, softInstId=softInstId, solId=solId, serverId=serverId, softId=softId,
                      mode=mode)
my_loop.end_loop()
