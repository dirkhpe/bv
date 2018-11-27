"""
This script will set the lifecycle status of a server. CMO servers will be set to "Inactive" if the server is installed
but no longer used. Status "Decommissioned" is used if the server is (physically) removed from the environment.
Status changes should be done for CMO servers only. FMO servers are managed in ESL. (but there is no validation on this)
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
    description="Set Life Cycle State for a server"
)
parser.add_argument('-s', '--hostName', type=str, required=True,
                    help='Please provide hostName to identify the server.')
parser.add_argument('-l', '--lifecycle', type=str, required=True,
                    choices=['Unknown', 'Plan', 'Build', 'Run', 'Active', 'Inactive', 'Decommissioned'],
                    help='Please provide lifecycle state (Unknown, Plan, Build, Run, Active, Inactive, Decommissioned)')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
mdb = murcsstore.Murcs(cfg)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

host = args.hostName
murcs_rec = mdb.get_server(host)
serverId = murcs_rec["serverId"]
serverprops = {}
if murcs_rec:
    print(murcs_rec)
    # Update existing server record to guarantee that all murcs fields are in serverprops.
    for k in murcs_rec:
        if k not in ignore:
            if murcs_rec[k]:
                serverprops[k] = murcs_rec[k]
    # Set Life Cycle State
    serverprops["lifeCycleState"] = args.lifecycle
    serverprops["parentServer"] = mdb.get_parentserver_dict(murcs_rec["parentServerId"])
    if murcs_rec["siteId"]:
        serverprops["site"] = mdb.get_site_dict(murcs_rec["siteId"])
    r.add_server(host, serverprops)
else:
    logging.error("Server {host} not found in MURCS".format(host=host))
