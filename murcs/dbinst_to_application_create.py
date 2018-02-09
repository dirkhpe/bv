"""
This script will connect a database instance to an application. The Database Software must exist. The database instance
(server to database software using schema name) will be created if required.

Note that during legacy data load, the database instance ID can have a link to a solution ID.
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
        Connect a database instance to an application. The (database) software must exist before. The database instance
        (server to database software using schema name) will be created if required.
        """
    )
    parser.add_argument('-i', '--instId', type=str, required=True,
                        help='Please provide database instance ID to identify the database (schema) on the server.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solId = args.solId
    instId = args.instId
    sol_rec = mdb.get_sol(solId)
    # Handle solution Instance for the solution
    if not mdb.get_solInst(solId):
        r.add_solutionInstance(sol_rec)
        mdb.recycle()
    solInst_rec = mdb.get_solInst(solId)
    softInst_rec = mdb.get_softInst_fromId(instId)
    if not softInst_rec:
        sys.exit("instance {instId} does not exist".format(instId=instId))
    solInst_id = solInst_rec["id"]
    softInst_id = softInst_rec["id"]
    serverId = softInst_rec["serverId"]
    softId = softInst_rec["softId"]
    if not mdb.get_solInstComp(solInst_id, softInst_id):
        r.add_solInstComp(solInst_rec, softInst_rec, solId, serverId, softId)
    mdb.close()
