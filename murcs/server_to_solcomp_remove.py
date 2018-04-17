"""
This script will remove a server to an solution component relation in MURCS.
The purpose is to remove a server from the Development / Quality or Production instance of a solution.
Only the softInstance will be removed. The solComp can still be connected to other servers.
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
        description="Remove a server from an application"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Compression'],
                        help='Please provide environment (Production, Quality, Development, Compression)')
    parser.add_argument('-m', '--mode', type=str, default='CMO',
                        choices=['CMO', 'FMO'],
                        help='Please specify CMO / FMO. CMO is default.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    mode = args.mode
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

    # Get Software for the Solution
    softId = "{solId} software".format(solId=solId)
    soft_rec = mdb.get_soft(softId)
    if not soft_rec:
        sys.exit("No Software for solution {s}".format(s=solName))

    # Get Link Software to Server for the Solution
    server_id = server_rec["id"]
    soft_id = soft_rec["id"]
    if mode == "FMO":
        softInstId = "{softId} {serverId} {env} {mode}".format(softId=softId, serverId=serverId,
                                                               env=args.env, mode=mode)
    else:
        softInstId = "{softId} {serverId} {env}".format(softId=softId, serverId=serverId, env=args.env)
    softInst_rec = mdb.get_softInst(soft_id, server_id, softInstId=softInstId)
    if softInst_rec:
        softInstId = softInst_rec["instId"]
        r.remove_softInst(serverId, softId, softInstId)
    elif mode != "FMO":
        # Legacy softInstId did not have env attached to the ID
        softInstId = "{softId} {serverId}".format(softId=softId, serverId=serverId)
        softInst_rec = mdb.get_softInst(soft_id, server_id, softInstId=softInstId)
        if softInst_rec:
            softInstId = softInst_rec["instId"]
            r.remove_softInst(serverId, softId, softInstId)
        else:
            sys.exit("No Software to Server Link for solution {s} and server {h}".format(s=solName, h=hostName))
    else:
        # FMO Mode, but softInst record not found.
        sys.exit("No FMO Software to Server Link for solution {s} and server {h}".format(s=solName, h=hostName))

    mdb.close()
