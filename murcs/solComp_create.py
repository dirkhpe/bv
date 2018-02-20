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
        description="Add a solution Component to a solution"
    )
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId for which a solution Component needs to be added.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Other'],
                        help='Select environment (Production, Development, Quality, Other)')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solId = args.solId
    sol_rec = mdb.get_sol(solId)
    if not sol_rec:
        sys.exit("Solution {solId} not found.".format(solId=solId))
    solInstId = my_env.get_solInstId(solId, args.env)
    solInst_rec = mdb.get_solComp(solInstId)
    if solInst_rec:
        sys.exit("Solution Component {solInstId} exists, not created.".format(solInstId=solInstId))
    else:
        r.add_solutionComponent(sol_rec, args.env)
    mdb.close()
