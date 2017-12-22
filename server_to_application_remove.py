"""
This script will remove a connection from a server to an application.
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
        description="Remove a connection from a server to an application"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solId = args.solId
    hostName = args.hostName
    sol_rec = mdb.get_sol(solId)
    server_rec = mdb.get_server(hostName)
    if not sol_rec:
        sys.exit("Solution {solId} not found.".format(solId=solId))
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=hostName))
    serverId = server_rec["serverId"]
    solName = sol_rec["solName"]

    # Get solution Instance for the solution
    solInst_rec = mdb.get_solInst(solId)
    if not solInst_rec:
        sys.exit("No Solution Instance for solution {s}".format(s=solName))

    # Get Software for the Solution
    softId = "{solId} software".format(solId=solId)
    soft_rec = mdb.get_soft(softId)
    if not soft_rec:
        sys.exit("No Software for solution {s}".format(s=solName))

    # Get Link Software to Server for the Solution
    server_id = server_rec["id"]
    soft_id = soft_rec["id"]
    softInst_rec = mdb.get_softInst(soft_id, server_id)
    if softInst_rec:
        softInstId = softInst_rec["instId"]
        r.remove_softInst(serverId, softId, softInstId)
    else:
        sys.exit("No Software to Server Link for solution {s} and server {h}".format(s=solName, h=hostName))

    mdb.close()
