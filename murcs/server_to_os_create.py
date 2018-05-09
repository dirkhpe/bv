"""
This script will add an OS to a server.
It will remove the current OS first.
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
    parser.add_argument('-o', '--softId', type=str, required=True,
                        help='Please provide softId of the OS to add.')
    parser.add_argument('-d', '--description', type=str, required=False,
                        help='Optionally provide additional OS version information')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    server_rec = mdb.get_server(args.hostName)
    if not server_rec:
        sys.exit("Server {h} not found...".format(h=args.hostName))
    # Find current OS
    softInst_rec = mdb.get_softInst_os(args.hostName)
    # Remove current OS if available
    if softInst_rec:
        r.remove_softInst(softInst_rec["serverId"], softInst_rec["softId"], softInst_rec["instId"])
    # Then add requested OS
    params = dict(
        instType='OperatingSystem'
    )
    if args.description:
        params["description"] = args.description
    r.add_softInst(args.softId, server_rec["serverId"], **params)
    mdb.close()
