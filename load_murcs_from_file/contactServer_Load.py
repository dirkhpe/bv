"""
This script will load a contact persons per server file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Contact person per server file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the contact person per server file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("Contact persons per server", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    email = xl.pop("email")
    role = xl.pop("role")
    serverId = xl.pop("serverId").lower()
    r.add_server_contact(serverId, email, role)
my_loop.end_loop()
