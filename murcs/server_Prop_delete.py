"""
This script will delete a Property from a server.
"""
import argparse
import datetime
import logging
import sys
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Delete a property from a server"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='Select property for Server')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    hostName = args.hostName
    server_rec = mdb.get_server(hostName)
    serverId = server_rec["serverId"]
    # Check if this is a known property for the server
    name_key = "{prop}_name".format(prop=args.name)
    try:
        propertyName = cfg["serverProps"][name_key]
    except KeyError:
        sys.exit("property identifier {prop} not found...".format(prop=args.name) )

    r.remove_server_property(serverId, propertyName)
    mdb.close()
