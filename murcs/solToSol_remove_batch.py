"""
This script will remove all solution to solution links from a file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Remove all Solution to Solution links"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file containing the solution to solution information.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Read the file
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("solToSol", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        fromSolId = xl.pop("fromSolId")
        toSolId = xl.pop("toSolId")
        solToSolId = xl.pop("solToSolId")
        r.remove_solToSol(solToSolId, fromSolId, toSolId)
    my_loop.end_loop()
