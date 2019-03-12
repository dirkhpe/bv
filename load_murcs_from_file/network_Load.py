"""
This script will load the network information.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib.murcs import *
from lib import murcsrest

iface_fields = ["duplex", "ifaceName", "macAddress", "negotiation", "netIfaceId", "speedMB"]

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Load the Network Information file into Murcs"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the Network Information file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("Network Information", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    serverId = xl.pop("serverId").lower()
    interfaceId = xl.pop("networkInterfaceId")
    ipAddress = xl.pop("ipAddress")
    payload_if = dict(
        networkInterfaceId=interfaceId,
        serverId=serverId
    )
    payload_ip = dict(
        serverNetworkInterfaceId=interfaceId,
        ipAddress=ipAddress
    )
    for k in xl:
        if pandas.notnull(xl[k]) and k not in excludedprops:
            if k in iface_fields:
                payload_if[k] = xl[k]
            else:
                payload_ip[k] = xl[k]
    r.add_serverNetIface(serverId, interfaceId, payload_if)
    r.add_serverNetIfaceIp(serverId, interfaceId, ipAddress, payload_ip)
my_loop.end_loop()
