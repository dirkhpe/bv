"""
This script will read the file murcs_servers and convert it to a Neo4J database.
"""

import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
softNamelbl = "softName"
softVersionlbl = "softVersion"
vendorlbl = "Vendor"
# Relations
name2vendor = "fromVendor"
version2name = "isSoft"

ignore = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "clientId"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
soft_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["soft"])
df = pandas.read_excel(soft_file)
# Get vendors
vendors = df.softVendor.unique()
vendor_d = {}
for vendor in vendors:
    if pandas.notnull(vendor):
        node_params = dict(
            name=vendor
        )
        vendor_d[vendor] = ns.create_node(vendorlbl, **node_params)

softName_d = {}
# Now handle all lines
my_loop = my_env.LoopInfo("Soft", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    softName = xl.pop("softName")
    softType = xl.pop("softType")
    softSubType = xl.pop("softSubType")
    try:
        soft_node = softName_d[softName]
    except KeyError:
        # Create soft node
        node_params = dict(
            name=softName,
            type=softType,
            subtype=softSubType
        )
        softName_d[softName] = ns.create_node(softNamelbl, **node_params)
    soft_node = softName_d[softName]
    # Link Vendor
    softVendor = xl.pop("softVendor")
    if pandas.notnull(softVendor):
        from_node = softName_d[softName]
        to_node = vendor_d[softVendor]
        ns.create_relation(from_node=soft_node, rel=name2vendor, to_node=to_node)
    # Create softNode
    node_params = {}
    for k in xl:
        if k not in ignore:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    softVersion_node = ns.create_node(softVersionlbl, **node_params)
    ns.create_relation(from_node=softVersion_node, rel=version2name, to_node=soft_node)
my_loop.end_loop()
