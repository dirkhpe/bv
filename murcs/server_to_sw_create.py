"""
This script will add a software to a server.
Unlike the server to OS server, it will not remove any existing connection.
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
        description="Connect a server to software (database)"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    parser.add_argument('-o', '--softId', type=str, required=True,
                        help='Please provide softId of the software to add.')
    parser.add_argument('-i', '--instance', type=str, required=False,
                        help='Optionally provide the instance schema. If schema used, then | is delimiter')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    hostName = args.hostName
    server_rec = mdb.get_server(hostName)
    if not server_rec:
        sys.exit("Server {h} not found.".format(h=hostName))
    serverId = server_rec["serverId"]

    # Then add requested OS
    params = dict(
        instType='Database'
    )
    if args.instance:
        params["instSubType"] = args.instance
    r.add_softInst(args.softId, serverId, **params)
    mdb.close()
