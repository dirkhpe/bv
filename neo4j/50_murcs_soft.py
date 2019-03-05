"""
This script will read the file software and convert it to a Neo4J database.
"""

import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import neostore
from lib.neostructure import *


cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
lcl = localstore.sqliteUtils(cfg)
ns = neostore.NeoStore(cfg)

soft_recs = lcl.get_table("software")

# Get vendors
query = "SELECT distinct softwareVendor from software"
res = lcl.get_query(query)
vendors = [rec["softwareVendor"] for rec in res]
vendor_d = {}
for vendor in vendors:
    if vendor:
        node_params = dict(
            name=vendor
        )
        vendor_d[vendor] = ns.create_node(lbl_vendor, **node_params)

softName_d = {}
# Now handle all lines
my_loop = my_env.LoopInfo("Soft", 20)
for trow in soft_recs:
    my_loop.info_loop()
    # Get excel row in dict format
    row = dict(trow)
    softName = row.pop("softwareName")
    softType = row.pop("softwareType")
    softSubType = row.pop("softwareSubType")
    try:
        soft_node = softName_d[softName]
    except KeyError:
        # Create soft node
        node_params = dict(
            name=softName,
            type=softType,
            subtype=softSubType
        )
        softName_d[softName] = ns.create_node(lbl_softName, **node_params)
    soft_node = softName_d[softName]
    # Link Vendor
    softVendor = row.pop("softwareVendor")
    if softVendor:
        from_node = softName_d[softName]
        to_node = vendor_d[softVendor]
        ns.create_relation(from_node=soft_node, rel=softName2vendor, to_node=to_node)
    # Create softNode
    node_params = {}
    for k in row:
        if k not in excludedprops:
            if row[k]:
                node_params[k] = row[k]
    softVersion_node = ns.create_node(lbl_softVersion, **node_params)
    ns.create_relation(from_node=softVersion_node, rel=softVersion2name, to_node=soft_node)
my_loop.end_loop()
