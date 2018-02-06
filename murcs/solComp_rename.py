"""
This script will add a solution Component to a solution in MURCS.
This is used to add a solution Component in another environment. The script will verify if the solution component
does not yet exist for the environment.
"""
import argparse
import logging
import sys
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="This procedure will update a solution Component to the standard name."
    )
    parser.add_argument('-l', '--solInstId', type=str, required=True,
                        help='Please provide the current (legacy) solInstId that needs to be renamed.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality'],
                        help='Select environment (Production, Development, Quality)')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solcomp_rec = mdb.get_solComp(args.solInstId)
    solId = solcomp_rec["solId"]
    sol_rec = mdb.get_sol(solId)
    if not sol_rec:
        sys.exit("Solution {solId} not found.".format(solId=solId))
    r.add_solutionComponent(sol_rec, args.env)
    mdb.close()
