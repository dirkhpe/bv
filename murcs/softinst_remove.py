"""
This script will remove a software (database) instance from a server.

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
        description="""
        Remove a software instance from a server.
        """
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostname of the server.')
    parser.add_argument('-d', '--softId', type=str, required=True,
                        help='Please provide the software ID.')
    parser.add_argument('-i', '--instance', type=str, required=True,
                        help='Please provide the instance ID to be removed')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    server_rec = mdb.get_server(args.hostName)
    if not server_rec:
        sys.exit("Server {h} not found...".format(h=args.hostName))
    soft_rec = mdb.get_soft(args.softId)
    if not soft_rec:
        sys.exit("Soft {h} not found...".format(h=args.softId))
    softInst_rec = mdb.get_softInst(soft_id=soft_rec["id"], server_id=server_rec["id"],
                                    softInstId=args.instance)
    if softInst_rec:
        r.remove_softInst(server_rec["serverId"], args.softId, args.instance)
    else:
        sys.exit("Instance {i} on server {h} for software {s} not found".format(h=args.hostName, s=args.softId,
                                                                                i=args.instance))
    mdb.close()
