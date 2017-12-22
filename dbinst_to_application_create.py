"""
This script will connect a database instance to an application. The Database Software must exist. The database instance
(server to database software using schema name) will be created if required.
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
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    parser.add_argument('-d', '--softId', type=str, required=True,
                        help='Please provide the (Database) software.')
    parser.add_argument('-n', '--dbName', type=str, required=True,
                        help='Please provide the Database name (mandatory).')
    parser.add_argument('-i', '--schema', type=str, required=False,
                        help='Please provide the schema name (optional).')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solId = args.solId
    hostName = args.hostName
    softId = args.softId
    dbName = args.dbName
    try:
        schema = args.schema
    except AttributeError:
        schema = False

    sol_rec = mdb.get_sol(solId)
    server_rec = mdb.get_server(hostName)
    soft_rec = mdb.get_soft(softId)
    if not sol_rec:
        sys.exit("Solution {solId} not found.".format(solId=solId))
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=hostName))
    if not soft_rec:
        sys.exit("Software {sw} not found.".format(sw=softId))
    serverId = server_rec["serverId"]

    # Handle solution Instance for the solution
    if not mdb.get_solInst(solId):
        r.add_solutionInstance(sol_rec)
        mdb.recycle()
    solInst_rec = mdb.get_solInst(solId)

    # Link Software to Server for the Solution
    server_id = server_rec["id"]
    soft_id = soft_rec["id"]
    softInstId = "{db}_{serverId}_{solId}".format(db=dbName, serverId=serverId, solId=solId)
    instSubType = dbName
    if schema:
        softInstId = schema + "_" + softInstId
        instSubType = instSubType + "|" + schema
    else:
        softInstId = "schema_" + softInstId

    if not mdb.get_softInst(soft_id, server_id, softInstId):
        r.add_software_instance(soft_rec, server_rec, softInstId, instSubType)
        mdb.recycle()
    softInst_rec = mdb.get_softInst(soft_id, server_id, softInstId)

    """

    # Create Solution Instance Component by linking softInst to SolInst
    softInst_id = softInst_rec["id"]
    solInst_id = solInst_rec["id"]
    if not mdb.get_solInstComp(solInst_id, softInst_id):
        r.add_solInstComp(solInst_rec, softInst_rec, solId, serverId, softId)
    """

    mdb.close()
