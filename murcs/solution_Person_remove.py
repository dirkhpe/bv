"""
This script will add a person to a solution.
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
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId for which a property needs to be added.')
    parser.add_argument('-p', '--email', type=str, required=True,
                        help='Please provide the person email address')
    parser.add_argument('-r', '--role', type=str, required=True,
                        help='Please provide the person role')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    r.remove_solution_contact(args.solId, args.email, args.role)
    mdb.close()
