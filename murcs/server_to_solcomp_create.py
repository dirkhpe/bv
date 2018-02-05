"""
This script will connect a server to an solution component in MURCS.
The purpose is to assign a server to the Development / Quality or Production instance of a solution.
Note that a server can be connected to more than one instance of a solution.
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
        description="Connect a server to an application"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    parser.add_argument('-a', '--solInstId', type=str, required=True,
                        help='Please provide solInstId to identify the application.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solInstId = args.solInstId
    hostName = args.hostName
    solcomp_rec = mdb.get_solComp(solInstId)
    server_rec = mdb.get_server(hostName)
    if not solcomp_rec:
        sys.exit("Solution Component {solInstId} not found.".format(solInstId=solInstId))
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=hostName))
    serverId = server_rec["serverId"]

    solId = solcomp_rec["solId"]
    # Handle Software for the Solution
    softId = "{solId} software".format(solId=solId)
    if not mdb.get_soft(softId):
        r.add_software_from_sol(sol_rec)
        mdb.recycle()
    soft_rec = mdb.get_soft(softId)

    # Link Software to Server for the Solution
    server_id = server_rec["id"]
    soft_id = soft_rec["id"]
    # softInst_rec = mdb.get_softInst(soft_id, server_id)
    if not mdb.get_softInst(soft_id, server_id):
        r.add_software_instance(soft_rec, server_rec)
        mdb.recycle()
    softInst_rec = mdb.get_softInst(soft_id, server_id)

    # Create Solution Instance Component by linking softInst to SolInst
    softInst_id = softInst_rec["id"]
    solInst_id = solInst_rec["id"]
    if not mdb.get_solInstComp(solInst_id, softInst_id):
        r.add_solInstComp(solInst_rec, softInst_rec, solInstId, serverId, softId)
    mdb.close()
