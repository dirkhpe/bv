"""
This script will remove a server.
"""
import argparse
import logging
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Remove a server"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    hostName = args.hostName
    server_rec = mdb.get_server(hostName)
    if server_rec:
        serverId = server_rec["serverId"]
        r.remove_server(serverId)
    else:
        logging.error("{h} not found...".format(h=hostName))

    mdb.close()
