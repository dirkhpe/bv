"""
This script will read a file and remove all network IP addresses and Interfaces defined in the file. First all IP
addresses will be removed. Then all interfaces will be removed.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Remove network interfaces from  Murcs"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the network interfaces file to load.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Read the file
    srv_ifaces = []
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("IPs", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        serverId = xl.pop("serverId")
        ifaceId = xl["netIfaceId"]
        ipAddress = xl["ipAddress"]
        r.remove_serverNetIfaceIp(serverId, ifaceId, ipAddress)
        # Remember ifaceId
        srv_iface = "{s}|{i}".format(s=serverId, i=ifaceId)
        if srv_iface not in srv_ifaces:
            srv_ifaces.append(srv_iface)
    my_loop.end_loop()

    # Now remove server Interfaces
    my_loop = my_env.LoopInfo("Interfaces", 20)
    for sif in srv_ifaces:
        my_loop.info_loop()
        serverId, ifaceId = sif.split("|")
        r.remove_serverNetIface(serverId, ifaceId)
    my_loop.end_loop()
