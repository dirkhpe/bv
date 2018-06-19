"""
This script will remove a server from a solution component relation in MURCS in FMO.
The purpose is to remove a server completely from the Development / Quality or Production instance of a solution.
In FMO this is done by removing all solcompinstance connections between server and solution component.
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
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solId = args.solId
    hostName = args.hostName
    fmo_id = "VPC."
    if hostName[:len(fmo_id)] != fmo_id:
        sys.exit("Hostname {h} appears not to be in VPC.".format(h=hostName))
    sol_rec = mdb.get_sol(solId)
    server_rec = mdb.get_server(hostName)
    if not sol_rec:
        sys.exit("Solution {solId} not found.".format(solId=solId))
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=hostName))
    serverId = server_rec["serverId"]
    solName = sol_rec["solName"]

    query = """
    SELECT server.serverId AS serverId, softinst.instId AS softInstId, soft.softId AS softId,
           solinst.solInstId AS solInstId, sol.solId AS solId
    FROM server
    INNER JOIN client on server.clientId=client.id
    INNER JOIN softinst on softinst.serverID=server.id
    INNER JOIN soft on softinst.softId=soft.id
    INNER JOIN solinstcomponent on solinstcomponent.softInstId=softinst.id
    INNER JOIN solinst on solinstcomponent.solInstId=solinst.id
    INNER JOIN sol on solinst.solId=sol.id
    WHERE client.clientId = "{clientId}"
    AND server.hostName = "{hostName}"
    AND sol.solId = "{solId}"
    AND solinst.environment = "{env}"
    AND solinstcomponent.validFrom is not null
    """.format(clientId=cfg["Murcs"]["clientId"],
               hostName=hostName,
               solId=solId,
               env=args.env)

    res = mdb.get_query(query)
    for rec in res:
        r.remove_solInstComp(rec["solInstId"], rec["softInstId"], rec["solId"], rec["serverId"], rec["softId"])

    mdb.close()
