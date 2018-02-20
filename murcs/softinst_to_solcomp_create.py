"""
This script will connect a software (database) instance to an solution component. The Software and the (database)
instance must exist.

Note that during legacy data load, the (database) instance ID can have a link to a solution ID.
This is an error  during initial load and prevents a database schema to be used by more than one application. However as
it is the ID of the instance, there is no easy way to correct this issue.

Therefore to connect a database instance to an application, it is mandatory to work with the instId.
Note that it is not possible to remove this link, as the softInstance cannot be removed and the solution instance
cannot be removed. Only the solcompinst record can be removed (manually)...
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
                        help='Please provide database instance ID to identify the database (schema) on the server.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Other'],
                        help='Please provide environment (Production, Quality, Development, Other)')
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
    if not mdb.get_solInstComp(solInst_id, softInst_id):
        r.add_solInstComp(solInstId, instId, solId, serverId, softId)
    mdb.close()
