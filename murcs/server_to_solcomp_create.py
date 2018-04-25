"""
This script will connect a server to an solution component in MURCS.
The purpose is to assign a server to the Development / Quality or Production instance of a solution.
Note that a server can be connected to more than one instance of a solution.

CMO and FMO are threaded differently.
In CMO a software is created for each application that needs to be coupled. Then a software instance is set-up on the
server for the application software, and this software instance is linked to the solution component.
In FMO the server OS is linked to the solution component, so no additional software for the application has to be
maintained.
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
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Other'],
                        help='Please provide environment (Production, Quality, Development, Other)')
    parser.add_argument('-m', '--mode', type=str, default='CMO',
                        choices=['CMO', 'FMO'],
                        help='Please specify CMO / FMO. CMO is default.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    mode = args.mode
    solInstId = my_env.get_solInstId(solId=args.solId, env=args.env)
    hostName = args.hostName
    solcomp_rec = mdb.get_solComp(solInstId)
    server_rec = mdb.get_server(hostName)
    if not solcomp_rec:
        sys.exit("Solution Component {solInstId} not found.".format(solInstId=solInstId))
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=hostName))
    serverId = server_rec["serverId"]
    solId = solcomp_rec["solId"]
    environment = solcomp_rec["environment"]

    if mode == "CMO":
        # Handle Software for the Solution
        softId = "{solId} software".format(solId=solId)
        if not mdb.get_soft(softId):
            r.add_software_from_sol(solcomp_rec)
            mdb.recycle()
        soft_rec = mdb.get_soft(softId)

        # Link Software to Server for the Solution
        server_id = server_rec["id"]
        soft_id = soft_rec["id"]
        softInstId = "{softId} {serverId} {env}".format(softId=softId, serverId=serverId, env=environment)
        if not mdb.get_softInst(soft_id, server_id, softInstId):
            params = dict(
                softInstId=softInstId,
                instSubType=environment
            )
            r.add_softInst(softId, serverId, **params)
            mdb.recycle()
        softInst_rec = mdb.get_softInst(soft_id, server_id, softInstId)
    elif mode == "FMO":
        # Get OS instance for the server
        softInst_rec = mdb.get_softInst_os(hostName)
        softId = softInst_rec["softId"]
        softInstId = softInst_rec["instId"]
    else:
        sys.exit("Unknown mode {m}".format(m=mode))


    # Create Solution Instance Component by linking softInst to SolInst
    softInst_id = softInst_rec["id"]
    solInst_id = solcomp_rec["id"]
    if not mdb.get_solInstComp(solInst_id, softInst_id):
        r.add_solInstComp(solInstId, softInstId, solId, serverId, softId, mode)
    mdb.close()
