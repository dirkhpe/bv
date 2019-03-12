"""
This script will load a contact person per solution file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Contact person per solution file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the contact person per solution file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename, converters={'solId': str})
my_loop = my_env.LoopInfo("Contact persons per solution", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    email = xl.pop("email")
    role = xl.pop("role")
    solId = xl.pop("solId")
    r.add_solution_contact(solId, email, role)
my_loop.end_loop()
