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
    solName = sol_rec["solName"]

    # Get solution Instance for the solution
    solInst_rec = mdb.get_solInst(solId)
    if not solInst_rec:
        sys.exit("No Solution Instance for solution {s}".format(s=solName))

    # Get Software to Server for the Solution
    server_id = server_rec["id"]
    soft_id = soft_rec["id"]
    softInstId = "{db}_{serverId}_{solId}".format(db=dbName, serverId=serverId, solId=solId)
    instSubType = dbName
    if schema:
        softInstId = "{schema}_{softInstId}".format(schema=schema, softInstId=softInstId)
        instSubType = instSubType + "|" + schema
    else:
        softInstId = "schema_" + softInstId

    softInst_rec = mdb.get_softInst(soft_id, server_id, softInstId)
    if softInst_rec:
        softInstId = softInst_rec["instId"]
        r.remove_softInst(serverId, softId, softInstId)
        logging.info("Link between solution {s} and server {h} over database {d} removed."
                     .format(s=solName, h=hostName, d=dbName))
    else:
        sys.exit("No Software to Server Link for solution {s} and server {h}".format(s=solName, h=hostName))

    mdb.close()
