"""
This script will load a person file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib.murcs import *
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load a Person file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the person file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("Persons", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    email = xl.pop("email")
    payload = dict(
        email=email
    )
    for k in xl:
        if pandas.notnull(xl[k]) and k not in excludedprops:
            payload[k] = xl[k]
    r.add_person(email, payload)
my_loop.end_loop()
