"""
This script will connect a server to an solution component in MURCS for FMO.
The purpose is to assign a server to the Development / Quality or Production instance of a solution.
Note that a server can be connected to more than one instance of a solution.
In FMO the server will be connected to the solution Component by linking the server OS to the solution component.
In FMO there will be a link from every other Software instance on the server to this solution component.

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
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    hostName = args.hostName
    solId = args.solId
    env = args.env
    solInstId = my_env.get_solInstId(solId=solId, env=env)
    solcomp_rec = mdb.get_solComp(solInstId)
    server_rec = mdb.get_server(hostName)
    if not solcomp_rec:
        sys.exit("Solution Component {solInstId} not found.".format(solInstId=solInstId))
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=hostName))
    serverId = server_rec["serverId"]

    # Get all software instances from the server
    query = """
    SELECT softinst.instId, soft.softId
    FROM softinst
    INNER JOIN soft ON soft.id=softinst.softId
    WHERE serverId={srv}
    """.format(srv=server_rec["id"])
    res = mdb.get_query(query)
    for rec in res:
        r.add_solInstComp(solInstId, rec["instId"], solId, serverId, rec["softId"], "FMO")
    mdb.close()
