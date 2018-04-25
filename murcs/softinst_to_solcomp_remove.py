"""
This script will remove a software (database) instance to an solution component. The Software and the (database)
instance must exist.

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
        description="""
        Connect a database instance to a solution component. The (database) software must exist before and the database
        instance (server to database software using schema name) must exist.
        """
    )
    parser.add_argument('-i', '--instId', type=str, required=True,
                        help='Please provide software (db) instance ID.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Compression'],
                        help='Please provide environment (Production, Quality, Development, Compression)')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solInstId = my_env.get_solInstId(solId=args.solId, env=args.env)
    solcomp_rec = mdb.get_solComp(solInstId)
    if not solcomp_rec:
        sys.exit("No environment {env} for Solution {solId}".format(solId=args.solId, env=args.env))
    instId = args.instId
    softInst_rec = mdb.get_softInst_fromId(instId)
    if not softInst_rec:
        sys.exit("instance {instId} does not exist".format(instId=instId))
    solInst_id = solcomp_rec["id"]
    solId = solcomp_rec["solId"]
    softInst_id = softInst_rec["id"]
    serverId = softInst_rec["serverId"]
    softId = softInst_rec["softId"]
    if mdb.get_solInstComp(solInst_id, softInst_id):
        r.remove_solInstComp(solInstId, instId, solId, serverId, softId)
    mdb.close()
