"""
This script will remove a person.
"""
import argparse
import logging
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Add a property to a solution Component to a solution"
    )
    parser.add_argument('-e', '--email', type=str, required=True,
                        help='Please provide email of the solution to be removed.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    r.remove_person(args.email)
    mdb.close()
