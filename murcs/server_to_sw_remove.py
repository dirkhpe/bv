"""
This script will remove a software instance from a server.
If softInstanceId is not provided, then every link between server and software will be removed.
If softInstanceId is provided, then only this softInstanceId is removed.

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
    parser.add_argument('-i', '--instanceId', type=str, required=False,
                        help='Optionally provide the Software instance ID.')
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

    softId = args.softId
    soft_rec = mdb.get_soft(softId)
    if not soft_rec:
        sys.exit("Software {s} not found".format(s=softId))

    if args.instanceId is None:
        # Find all softInstanceId records to remove.
        query = """
        SELECT instId
        FROM softinst
        WHERE serverId={srv} AND softId={soft}
        """.format(srv=server_rec["id"], soft=soft_rec["id"])
        res = mdb.get_query(query)
        for rec in res:
            r.remove_softInst(server_rec["serverId"], softId, rec["instId"])
    else:
        softInstId = args.instanceId
        r.remove_softInst(server_rec["serverId"], softId, softInstId)

    mdb.close()
