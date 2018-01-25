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
softTypelbl = "softType"
softSubTypelbl = "softSubType"
softVersionlbl = "softVersion"
vendorlbl = "Vendor"
# Relations
subType2Type = "isType"
name2subType = "group"
name2vendor = "fromVendor"
name2version = "hasVersion"

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
# Get softTypes
softTypes = df.softType.unique()
softType_d = {}
for softType in softTypes:
    node_params = dict(
        name=softType
    )
    softType_d[softType] = ns.create_node(softTypelbl, **node_params)
# Get softSubType
softSubTypes = df.softSubType.unique()
softSubType_d = {}
for softSubType in softSubTypes:
    node_params = dict(
        name=softSubType
    )
    softSubType_d[softSubType] = ns.create_node(softSubTypelbl, **node_params)
# Get softName
softNames = df.softName.unique()
softName_d = {}
for softName in softNames:
    node_params = dict(
        name=softName
    )
    softName_d[softName] = ns.create_node(softNamelbl, **node_params)

# Now handle all lines
my_loop = my_env.LoopInfo("Soft", 20)
for row in df.iterrows():
    my_loop.info_loop()
    # Get excel row in dict format
    xl = row[1].to_dict()
    softName = xl.pop("softName")
    # Link Vendor
    softVendor = xl.pop("softVendor")
    if pandas.notnull(softVendor):
        from_node = softName_d[softName]
        to_node = vendor_d[softVendor]
        ns.create_relation(from_node=from_node, rel=name2vendor, to_node=to_node)
    # Link Type - Subtype
    softType = xl.pop("softType")
    softSubType = xl.pop("softSubType")
    rel = subType2Type
    from_node = softSubType_d[softSubType]
    to_node = softType_d[softType]
    ns.create_relation(from_node=from_node, rel=rel, to_node=to_node)
    # Link Name to SubType
    rel = name2subType
    from_node = softName_d[softName]
    to_node = softSubType_d[softSubType]
    ns.create_relation(from_node=from_node, rel=rel, to_node=to_node)
    # Create softNode
    node_params = {}
    for k in xl:
        if k not in ignore:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    softVersion_node = ns.create_node(softVersionlbl, **node_params)
    ns.create_relation(from_node=softName_d[softName], rel=name2version, to_node=softVersion_node)
my_loop.end_loop()
