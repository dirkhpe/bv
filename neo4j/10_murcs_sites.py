"""
This script will read the person and convert it to a Neo4J database.
"""

import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib.neostructure import *
from lib import neostore

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
lcl = localstore.sqliteUtils(cfg)
ns = neostore.NeoStore(cfg)

sites = lcl.get_table("site")
region_d = {}
country_d = {}
site_node_d = {}
my_loop = my_env.LoopInfo("Sites", 20)
for site in sites:
    row = dict(site)
    # Get site links
    region = row.pop("region")
    if region:
        region_d[row["siteId"]] = region
    country = row.pop("country")
    if country:
        country_d[row["siteId"]] = country
    # Site link information is handled and removed from row, now handle remaining columns
    node_params = {}
    for k in row:
        if k not in excludedprops:
            if row[k]:
                node_params[k] = row[k]
    site_node_d[row["siteId"]] = ns.create_node(lbl_site, **node_params)
    my_loop.info_loop()
my_loop.end_loop()

# Link to Region
region_node_d = {}
my_loop = my_env.LoopInfo("Link to Region", 20)
for k in region_d:
    try:
        region_node = region_node_d[region_d[k]]
    except KeyError:
        node_params = dict(
            region=region_d[k]
        )
        region_node_d[region_d[k]] = ns.create_node(lbl_region, **node_params)
        region_node = region_node_d[region_d[k]]
    ns.create_relation(from_node=site_node_d[k], rel=site2region, to_node=region_node)
    my_loop.info_loop()
my_loop.end_loop()

# Link to Country
country_node_d = {}
my_loop = my_env.LoopInfo("Link to Country", 20)
for k in country_d:
    try:
        country_node = country_node_d[country_d[k]]
    except KeyError:
        node_params = dict(
            country=country_d[k]
        )
        country_node_d[country_d[k]] = ns.create_node(lbl_country, **node_params)
        country_node = country_node_d[country_d[k]]
    ns.create_relation(from_node=site_node_d[k], rel=site2country, to_node=country_node)
    my_loop.info_loop()
my_loop.end_loop()
