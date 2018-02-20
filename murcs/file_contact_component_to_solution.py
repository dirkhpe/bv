"""
This script will read a file to rearrange all contacts from solution components to solutions.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="File to process into Murcs"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file to load.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Read the file
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("Servers", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        solId = xl["solId"]
        solInstId = xl["solInstId"]
        personId = xl["email"]
        role = xl["role"]
        r.remove_solComp_contact(solId, solInstId, personId, role)
        r.add_solution_contact(solId, personId, role)
    my_loop.end_loop()
