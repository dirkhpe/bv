"""
This script will load softInst file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Load a SoftInst file into Murcs"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the softInst file to load. The file must have softId and serverId, and can'
                             ' have instType (default: Application), instSubType (DB Schema or environment) OR '
                             'softInstId')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Read the file
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("SoftInst", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        softId = xl.pop("softId")
        serverId = xl.pop("serverId")
        params = {}
        for k in xl:
            if pandas.notnull(xl[k]):
                params[k] = xl[k]
        r.add_softInst_calc(softId, serverId, **params)
    my_loop.end_loop()
