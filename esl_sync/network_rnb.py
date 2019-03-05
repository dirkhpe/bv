"""
This script will sync MURCS IP addresses with Runbook IP addresses.
BYOIP address for ITO managed servers is not included from the start in ESL.
If it is missing, then BYOIP from Runbook is added.
It will remove IP addresses from MURCS that are no longer in NAT.
"""
import argparse
import logging
import pandas
from lib import localstore
from lib import my_env
from lib import murcsrest

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Synchronize MURCS IP info additional BYOIP from Runbook."
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the file with Runbook IP info..')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
lcl = localstore.sqliteUtils(cfg)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

src_name = "RNB"
esl_prefix = "ESL|auto detected - change|"

# Find Interface configs in MURCS.
net_in_murcs = []
net_in_nat = []
query = """
SELECT distinct server.serverId as serverId, sni.networkInterfaceId as netIfaceId
FROM server
INNER JOIN netiface sni on sni.serverId=server.serverId
WHERE sni.netIfaceId like "{src}|%"
   OR sni.netIfaceId like "{esl_prefix}%";
""".format(src=src_name, esl_prefix=esl_prefix)

res = lcl.get_query(query)
for rec in res:
    lbl = "{s}|{id}".format(s=rec["serverId"], id=rec["netIfaceId"])
    net_in_murcs.append(lbl)

# Read the Runbook report to load/update IP addresses in MURCS.
df = pandas.read_excel(args.filename, sheet_name="Server Order", header=1)
my_loop = my_env.LoopInfo("Runbook Interfaces", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    if pandas.notnull(xl["Server Name"]):
        serverId = my_env.fmo_serverId(xl["Server Name"])
        srv_rec = lcl.get_server(serverId)
        if srv_rec:
            if pandas.notnull(xl["BYOIP"]):
                ifaceName = "BYOIP"
                byoip = xl[ifaceName]
                esl_id = "{serverId}|{esl_prefix}{ip}".format(serverId=serverId, esl_prefix=esl_prefix, ip=byoip)
                if esl_id not in net_in_murcs:
                    lbl = "{src}|BYOIP|{ip}".format(src=src_name, ip=byoip)
                    rnb_id = "{serverId}|{lbl}".format(serverId=serverId, lbl=lbl)
                    if rnb_id not in net_in_murcs:
                        props = dict(
                            serverId=serverId,
                            networkInterfaceId=lbl,
                            interfaceName=ifaceName
                        )
                        r.add_serverNetIface(serverId, lbl, props)
                        props = dict(
                            name=ifaceName
                        )
                        r.add_serverNetIfaceIp(serverId, lbl, byoip, props)

            if pandas.notnull(xl["Public IP"]):
                ifaceName = "Public IP"
                public_ip = xl[ifaceName]
                lbl = "{src}|Public IP|{ip}".format(src=src_name, ip=public_ip)
                rnb_id = "{serverId}|{lbl}".format(serverId=serverId, lbl=lbl)
                if rnb_id not in net_in_murcs:
                    props = dict(
                        serverId=serverId,
                        networkInterfaceId=lbl,
                        interfaceName=ifaceName
                    )
                    r.add_serverNetIface(serverId, lbl, props)
                    props = dict(
                        name=ifaceName
                    )
                    r.add_serverNetIfaceIp(serverId, lbl, public_ip, props)
my_loop.end_loop()
