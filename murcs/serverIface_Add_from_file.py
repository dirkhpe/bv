"""
This script will read a file and add all IP addresses from the file. Columns need to be serverId and "IP discovered"
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest, murcsstore

dc_names = ["EMEA-DE-Frankfurt-eshelter-B"]
ip_labels = ["Primary IP", "auto detected - change"]

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Add IP information from file into MURCS."
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file with IP info..')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    src_name = "ESL"

    # Read the file to load information in MURCS.
    df = pandas.read_excel(args.filename, sheet_name="NicolasDiscovery")
    my_loop = my_env.LoopInfo("IP Addresses", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        if pandas.notnull(xl["ServerID"]) and pandas.notnull(xl["IP discovered"]):
            serverId = xl["ServerID"]
            if mdb.get_server_from_serverId(serverId):
                lbl = "Discovery"
                src_name = "PingTool"
                ipAddress = xl["IP discovered"]
                ifaceId = "{src}|{lbl}|{ip}".format(src=src_name, lbl=lbl, ip=ipAddress)
                srvlbl = "{s}|{id}".format(s=serverId, id=ifaceId)
                props = dict(
                    serverId=serverId,
                    networkInterfaceId=ifaceId,
                    interfaceName=lbl
                )
                r.add_serverNetIface(serverId, ifaceId, props)
                props = dict(
                    name=lbl
                )
                r.add_serverNetIfaceIp(serverId, ifaceId, ipAddress, props)
            else:
                logging.error("Server ID {sid} not found in MURCS".format(sid=serverId))
    my_loop.end_loop()
