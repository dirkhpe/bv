"""
This script will remove a software (database) instance from a server.

"""
import argparse
import logging
import sys
from lib import my_env
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="""
        Remove a software instance from a server.
        """
    )
    parser.add_argument('-s', '--serverId', type=str, required=True,
                        help='Please provide serverId of the server.')
    parser.add_argument('-d', '--softId', type=str, required=True,
                        help='Please provide the software ID.')
    parser.add_argument('-i', '--instance', type=str, required=True,
                        help='Please provide the instance ID to be removed')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    r.remove_softInst(args.serverId, args.softId, args.instance)
