"""
This script will add Service description to a server. A service description explains why a server has been ordered but
not used at this time, or replaced by another server.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest, murcsstore

ignore = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "clientId", "service"]

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Provide Service description for the server."
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide the hostName.')
    parser.add_argument('-d', '--description', type=str, required=True,
                        help="Please provide a Service Description for this server")
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    hostName = args.hostName
    server_rec = mdb.get_server(hostName)
    serverprops = {}
    if server_rec:
        serverprops["service"] = args.description
        for k in server_rec:
            if k not in ignore:
                if len(server_rec[k]) > 0:
                    serverprops[k] = server_rec[k]
    r.add_server(server_rec["serverId"], serverprops)
    mdb.close()
