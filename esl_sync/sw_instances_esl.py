"""
This script will sync software from ESL with MURCS. This does not include OS. OS is handled from servers_esl.py.
Software in ESL is defined in the categories from whitelist. Note that "engine" is in the blacklist. This means that
for every engine there needs to be a corresponding software component. For example, a DB engine needs to have an entry
with SW Category database.
It can happen that a database is removed and not discovered in ESL. In this case the database will be removed from
MURCS.

It will remove software implementations from MURCS that are no longer in ESL.
"""
import argparse
import logging
import pandas
from lib import localstore
from lib import my_env
from lib import murcsrest

dc_names = ["EMEA-DE-Frankfurt-eshelter-B"]
whitelist = ["database", "sap/erp", "webcomponent"]
blacklist = ["engine", "os", "standard software"]

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Synchronize MURCS info with ESL information."
)
parser.add_argument('-f', '--filename', type=str, required=True,
                    help='Please provide the file with ESL Server IP info..')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
lcl = localstore.sqliteUtils(cfg)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

# Get ESL to softId translation
sw_tx = {}
bv_tx_file = cfg["Main"]["translate"]
df = pandas.read_excel(bv_tx_file, sheet_name="sw")
for row in df.iterrows():
    xl = row[1].to_dict()
    if pandas.notnull(xl["Solution Category"]):
        lbl = "{cat}|{name}|{version}".format(cat=xl["Solution Category"],
                                              name=xl["Solution Name"],
                                              version=xl["Software/Firmware Version"])
        sw_tx[lbl] = xl["softId"]
logging.info("{c} Software Instances translations found for Murcs".format(c=len(sw_tx)))

src_name = "ESL"
# Find Software Instance configurations in MURCS.
swinst_in_murcs = []
swinst_in_esl = []
query = """
SELECT distinct server.hostName as hostName, server.serverId as serverId, softinst.softwareInstanceId as instId
FROM softinst
INNER JOIN server on server.id = softinst.serverId
WHERE softinst.softwareInstanceId LIKE "{src}_%"
""".format(src=src_name)

res = lcl.get_query(query)
for rec in res:
    swinst_in_murcs.append(rec["instId"])
logging.info("{c} Software Instances found in Murcs".format(c=len(swinst_in_murcs)))

# Read the ESL report to load/update software instances in MURCS.
df = pandas.read_excel(args.filename)
my_loop = my_env.LoopInfo("ESL Interfaces", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Only handle systems from VPC.
    if xl["DC Name"] in dc_names:
        category = xl["Solution Category"]
        if pandas.notnull(category):
            if category in whitelist:
                my_loop.info_loop()
                serverId = my_env.fmo_serverId(xl["System Name"])
                lbl = "{cat}|{name}|{version}".format(cat=xl["Solution Category"],
                                                      name=xl["Solution Name"],
                                                      version=xl["Software/Firmware Version"])
                try:
                    softId = sw_tx[lbl]
                except KeyError:
                    logging.error("No translation to softId for {lbl}".format(lbl=lbl))
                else:
                    # softId can have _ as part of the name, so instId construction is not optimal since _ cannot
                    # be used as a field delimiter.
                    instId = "{src}_{softId}_{sys}".format(src=src_name, softId=softId, sys=serverId)
                    swinst_in_esl.append(instId)
                    if instId not in swinst_in_murcs:
                        props = dict(
                            softInstId=instId,
                            instType=xl["Solution Category"],
                            patchLevel=xl["Software/Firmware Version"]
                        )
                        if pandas.notnull(xl["Instance Name"]):
                            props["instanceSubType"] = xl["Instance Name"]
                        if pandas.notnull(xl["Instance Status"]):
                            props["description"] = xl["Instance Status"]
                        r.add_softInst_calc(softId, serverId, **props)
my_loop.end_loop()

# Now remove entries in MURCS that are no longer in ESL
rem_instances = [lbl for lbl in swinst_in_murcs if lbl not in swinst_in_esl]
for lbl in rem_instances:
    # _ cannot be used as field delimiter to split src, softId, serverId
    # Remove src from label, then split on _VPC. identifier
    soft_server = lbl[len(src_name)+1:]
    ss_delim_pos = soft_server.find("_VPC.")
    softId = soft_server[:ss_delim_pos]
    serverId = soft_server[ss_delim_pos+1:]
    r.remove_softInst(serverId, softId, lbl)
