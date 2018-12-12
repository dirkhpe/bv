"""
This script will read a file and set the domain information for CMO servers.
Domain information from FMO servers is read from ESL.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsstore
from lib import murcsrest

ignore = my_env.server_ignore
# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Set Domain for a server"
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the server file to load.')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
mdb = murcsstore.Murcs(cfg)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Read the file
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("Servers", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    if pandas.notnull(xl["ServerID"]) and pandas.notnull(xl["Domain"]):
        serverId = xl["ServerID"]
        murcs_rec = mdb.get_server_from_serverId(serverId)
        if murcs_rec:
            serverprops = {}
            # Update existing server record to guarantee that all murcs fields are in serverprops.
            for k in murcs_rec:
                if k not in ignore:
                    if murcs_rec[k]:
                        serverprops[k] = murcs_rec[k]
            # Set Life Cycle State
            serverprops["domain"] = xl["Domain"][1:]
            serverprops["clientId"] = cfg["Murcs"]["clientId"]
            if murcs_rec["parentServerId"]:
                serverprops["parentServer"] = mdb.get_parentserver_dict(murcs_rec["parentServerId"])
            try:
                serverprops["site"] = mdb.get_site_dict(murcs_rec["siteId"])
            except KeyError:
                pass
            r.add_server(serverId, serverprops)
        else:
            logging.error("Server {host} not found in MURCS".format(host=serverId))
