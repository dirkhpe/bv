"""
This script will sync MURCS Servers with ESL Report. It will load or update all servers in VPC datacenter into MURCS.
A list of servers in MURCS but no longer in VPC will be created.
"""
import argparse
import logging
import pandas
from lib import localstore
from lib import my_env
from lib import murcsrest

ignore = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "clientId", "siteId", "version", "dataQuality",
          "parentServerId"]

dc_names = ["EMEA-DE-Frankfurt-eshelter-B"]

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Synchronize MURCS Servers with ESL information."
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the file with ESL Server info..')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
lcl = localstore.sqliteUtils(cfg)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Get BellaVista to softId translation for OS
sw_tx = {}
bv_tx_file = cfg["Main"]["translate"]
df = pandas.read_excel(bv_tx_file, sheet_name="os")
for row in df.iterrows():
    esl = row[1].to_dict()
    sw_tx[esl["BellaVistaOs"]] = esl["softId"]

# Get MURCS - ESL mapping
m2e = {}
m2e_fixed = {}
m2e_file = cfg["Murcs"]["murcs2esl_server"]
df = pandas.read_excel(m2e_file)
for row in df.iterrows():
    esl = row[1].to_dict()
    if pandas.notnull(esl["esl"]):
        m2e[esl["murcs"]] = esl["esl"]
    elif pandas.notnull(esl["fixed"]):
        m2e_fixed[esl["murcs"]] = esl["fixed"]

srv_in_esl = []
# Read the ESL report to load/update systems in MURCS.
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("ESL", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    esl = row[1].to_dict()
    # Only handle systems from VPC.
    if esl["DC Name"] in dc_names:
        serverId = my_env.fmo_serverId(esl["System Name"])
        srv_in_esl.append(serverId)
        # Create dictionary with info from ESL
        serverprops = dict(
            hostName=serverId,
            serverId=serverId,
            site=dict(siteId=esl["DC Name"])
        )
        # Add fixed strings to dictionary
        for k in m2e_fixed:
            serverprops[k] = m2e_fixed[k]
        # Add variable ESL information to dictionary
        for k in m2e:
            if pandas.notnull(esl[m2e[k]]):
                if k == "memorySizeInByte":
                    serverprops[k] = esl[m2e[k]] * 1024 * 1024
                elif k == "clockSpeedGhz":
                    serverprops[k] = esl[m2e[k]] // 1000
                elif k == "serverType":
                    if esl[m2e[k]] == "yes":
                        serverprops[k] = "VIRTUAL"
                    else:
                        serverprops[k] = "PHYSICAL"
                else:
                    # if null then k will not be added to serverprops so value in Murcs will be set to blank
                    serverprops[k] = esl[m2e[k]]
        # Check for update or new record
        murcs_rec = lcl.get_server(serverId)
        initialize_os_id = "to be defined"
        os_id = initialize_os_id
        if murcs_rec:
            # Remember softId for OS
            soft_rec = lcl.get_softInst_os(serverId)
            if soft_rec:
                os_id = soft_rec["softwareId"]
            # Update existing server record to guarantee that all murcs fields are in serverprops.
            for k in murcs_rec:
                if not ((k in ignore) or (k in m2e) or (k in m2e_fixed)):
                    if pandas.notnull(murcs_rec[k]):
                        serverprops[k] = murcs_rec[k]
            # Now find fields that are updated or changed - murcs_rec is what we know. Does serverprops add info?
            # Check for new fields in ESL not yet in Murcs
            # I cannot find fields in Murcs no longer in ESL.
            updates = []
            for k in serverprops:
                if k not in ["site"]:
                    # Change in site is not picked up.
                    try:
                        if str(serverprops[k]) != str(murcs_rec[k]):
                            # Update in field
                            updates.append((k, serverprops[k]))
                    except KeyError:
                        # New field, not yet in Murcs
                        logging.info("New field {p}".format(p=(k, serverprops[k])))
                        updates.append((k, serverprops[k]))
            if len(updates) > 0:
                logging.info("Update on {s}: {u}".format(s=serverprops["hostName"], u=updates))
                r.add_server(serverId, serverprops)
        else:
            r.add_server(serverId, serverprops)

        # Add OS if new or Update compared to previous version
        os = esl["OS Version"]
        try:
            softId = sw_tx[os.strip()]
        except KeyError:
            logging.error("OS Version {os} cannot be translated to softId".format(os=os))
        else:
            # Check if this is update OS or new OS definition. Don't update if OK already
            if os_id == initialize_os_id:
                # No OS found for this server in MURCS
                params = dict(
                    instType='OperatingSystem'
                )
                r.add_softInst_calc(softId, serverId, **params)
            elif os_id != softId:
                logging.info("Server {h} new OS {s} (from {o})".format(h=serverId, s=softId, o=os_id))
                params = dict(
                    instType='OperatingSystem'
                )
                r.add_softInst_calc(softId, serverId, **params)
my_loop.end_loop()

# Now find servers in MURCS that are not in ESL.
query = "SELECT hostName, serverId FROM server WHERE serverId LIKE 'VPC.%'"
res = lcl.get_query(query)
for rec in res:
    if rec["serverId"] not in srv_in_esl:
        logging.error("Server {h} in MURCS, not in ESL.".format(h=rec["hostName"]))
        r.remove_server(rec["serverId"])
