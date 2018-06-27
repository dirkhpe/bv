"""
This script will sync the Caslano VM List with CPU count in MURCS. CPU in MURCS means the total number of (virtual)
CPUs. In case the CPU has been updated, then a server property will be set as well.

"""
import argparse
import datetime
import logging
import csv
import sys
from lib import my_env
from lib import murcsrest, murcsstore

ignore = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "clientId", "siteId"]

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Update CPU Count in MURCS from VMWare extract."
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file with Server info..')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    csv.register_dialect('tabdelim', delimiter='\t')
    with open(args.filename, newline='\r\n') as f:
        reader = csv.DictReader(f, dialect='tabdelim')

        my_loop = my_env.LoopInfo("VMWare List", 20)
        for line in reader:
            my_loop.info_loop()
            serverId = line["Name"]
            server_rec = mdb.get_server_from_serverId(serverId)
            if server_rec:
                if str(server_rec["cpuCount"]) != line["CPUs"]:
                    # Update record only if cpuCount is changed.
                    payload = {}
                    if server_rec["siteId"] is not None:
                        siteId = mdb.get_name_id("site", "siteId", server_rec["siteId"])
                        if siteId:
                            payload["site"] = dict(siteId=siteId)
                        else:
                            logging.fatal("Could not find Site ID for id {id}".format(id=server_rec["siteId"]))
                            sys.exit(1)
                    if server_rec["parentServerId"] is not None:
                        parentServer = mdb.get_name_id("server", "serverId", server_rec["parentServerId"])
                        if parentServer:
                            payload["parentServer"] = dict(serverId=parentServer)
                        else:
                            logging.fatal("Couldn't find Parent ID {id}".format(id=server_rec["parentServerId"]))
                            sys.exit(1)
                    for k in server_rec:
                        # coreCount has been added to the ignore list so that it gets dropped.
                        if (k not in ignore) and (server_rec[k] is not None):
                            if k == "primaryIP":
                                payload["primaryIPAddress"] = server_rec[k]
                            else:
                                payload[k] = server_rec[k]
                    payload["cpuCount"] = line["CPUs"]
                    r.add_server(serverId=serverId, payload=payload)
                # Always confirm that cpuCount has been set.
                payload = dict(
                    propertyName="vCPU Count",
                    propertyValue=line["CPUs"],
                    description="CPU Count update from VMWare - {now:%Y-%m-%d}".format(now=datetime.datetime.now())
                )
                r.add_server_property(server_rec["serverId"], payload)
                cnt = my_loop.info_loop()
            else:
                logging.error("{sid} not found in MURCS".format(sid=serverId))

        my_loop.end_loop()
    mdb.close()
