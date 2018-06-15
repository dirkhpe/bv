"""
This script will load a solution file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Load a Server file into Murcs"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the solution file to load.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Read the file
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("Solutions", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        solId = xl["solutionId"]
        xl.pop("clientId")
        payload = dict(
            solId=solId
        )
        for k in xl:
            if pandas.notnull(xl[k]):
                payload[k] = xl[k]
        r.add_sol(solId, payload)
    my_loop.end_loop()
