"""
This script will add a person to a server.
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
        description="Add a person to a server"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide the server (hostname).')
    parser.add_argument('-p', '--email', type=str, required=True,
                        help='Please provide the person email address')
    parser.add_argument('-r', '--role', type=str, required=True,
                        help='Please provide the person role')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    server_rec = mdb.get_server(args.hostName)
    if server_rec:
        r.add_server_contact(server_rec["serverId"], args.email, args.role)
    else:
        sys.exit("Server {h} not found...".format(h=args.hostName))
    mdb.close()
