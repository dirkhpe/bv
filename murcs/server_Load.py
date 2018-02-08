"""
This script will load a server file.
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
                        help='Please provide the server file to load.')
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
        serverId = xl.pop("serverId").lower()
        payload = dict(
            serverId=serverId
        )
        for k in xl:
            if pandas.notnull(xl[k]):
                if k == "hostName":
                    payload[k] = xl[k].lower()
                else:
                    payload[k] = xl[k]
        r.add_server(serverId, payload)
    my_loop.end_loop()
