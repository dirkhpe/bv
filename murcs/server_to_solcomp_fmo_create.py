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
from lib import localstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Connect a server to an application"
    )
    parser.add_argument('-s', '--serverId', type=str, required=True,
                        help='Please provide serverId to identify the server.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Other'],
                        help='Please provide environment (Production, Quality, Development, Other)')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    lcl = localstore.sqliteUtils(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    serverId = args.serverId
    solId = args.solId
    env = args.env
    solInstId = my_env.get_solInstId(solId=solId, env=env)
    solcomp_rec = lcl.get_solComp(solInstId)
    server_rec = lcl.get_server(serverId)
    if not solcomp_rec:
        sys.exit("Solution Component {solInstId} not found.".format(solInstId=solInstId))
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=serverId))

    # Get all software instances from the server
    query = """
    SELECT softinst.softwareInstanceId as instId, software.softwareId as softId
    FROM softinst
    INNER JOIN software ON software.softwareId=softinst.softwareId
    WHERE softinst.serverId="{srv}"
    """.format(srv=serverId)
    res = lcl.get_query(query)
    for rec in res:
        r.add_solInstComp(solInstId, rec["instId"], solId, serverId, rec["softId"], "FMO")
    lcl.close()
