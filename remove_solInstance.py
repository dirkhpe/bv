"""
This script will remove a solutionInstance from a solution in MURCS
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
        description="Remove a solution Instance from a solution"
    )
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId for which instance ID needs to be removed.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solId = args.solId
    sol_rec = mdb.get_sol(solId)
    if not sol_rec:
        sys.exit("Solution {solId} not found.".format(solId=solId))
    solInst_rec = mdb.get_solInst(sol_rec["solId"])
    if not solInst_rec:
        logging.info("Solution *{solId}* doesn't have an instance.".format(solId=solId))
    else:
        r.remove_solutionInstance(solId, solInst_rec["solInstId"])
    mdb.close()
