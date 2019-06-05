"""
This script will remove a server from a solution component relation in MURCS in FMO.
The purpose is to remove a server completely from the Development / Quality or Production instance of a solution.
In FMO this is done by removing all solcompinstance connections between server and solution component.
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
        description="Remove a server from an application"
    )
    parser.add_argument('-s', '--serverId', type=str, required=True,
                        help='Please provide serverId to identify the server.')
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId to identify the application.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Compression'],
                        help='Please provide environment (Production, Quality, Development, Compression)')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    lcl = localstore.sqliteUtils(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solId = args.solId
    serverId = args.serverId

    query = """
    SELECT server.serverId AS serverId, softinst.softwareInstanceId AS softInstId, software.softwareId AS softId,
           solinst.solutionInstanceId AS solInstId, solution.solutionId AS solId
    FROM server
    INNER JOIN softinst on softinst.serverId=server.serverId
    INNER JOIN software on softinst.softwareId=software.softwareId
    INNER JOIN solinstcomp on solinstcomp.softwareInstanceId=softinst.softwareInstanceId
    INNER JOIN solinst on solinstcomp.solutionInstanceId=solinst.solutionInstanceId
    INNER JOIN solution on solinst.solutionId=solution.solutionId
    WHERE server.serverId = "{serverId}"
    AND solution.solutionId = "{solId}"
    AND solinst.environment = "{env}"
    AND solinstcomp.validFrom is not null
    """.format(serverId=serverId,
               solId=solId,
               env=args.env)

    res = lcl.get_query(query)
    for rec in res:
        r.remove_solInstComp(rec["solInstId"], rec["softInstId"], rec["solId"], rec["serverId"], rec["softId"])
    lcl.close()
