"""
This script will read the file murcs_sites and convert it to a Neo4J database.
"""

import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
sitelbl = "Site"
regionlbl = "Region"
countrylbl = "Country"
# Relations
site2region = "inRegion"
site2country = "inCountry"

ignore = ["changedAt", "changedBy", "createdAt", "createdBy", "version", "clientId"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
sites_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["sites"])
df = pandas.read_excel(sites_file)
region_d = {}
country_d = {}
site_node_d = {}
my_loop = my_env.LoopInfo("Sites", 20)
for row in df.iterrows():
    # Get excel row in dict format
    xl = row[1].to_dict()
    # Get site links
    region = xl.pop("region")
    if pandas.notnull(region):
        region_d[xl["siteId"]] = region
    country = xl.pop("country")
    if pandas.notnull(country):
        country_d[xl["siteId"]] = country
    # Site link information is handled and removed from row, now handle remaining columns
    node_params = {}
    for k in xl:
        if k not in ignore:
            if pandas.notnull(xl[k]):
                node_params[k] = xl[k]
    site_node_d[xl["siteId"]] = ns.create_node(sitelbl, **node_params)
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
        region_node_d[region_d[k]] = ns.create_node(regionlbl, **node_params)
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
        country_node_d[country_d[k]] = ns.create_node(countrylbl, **node_params)
        country_node = country_node_d[country_d[k]]
    ns.create_relation(from_node=site_node_d[k], rel=site2country, to_node=country_node)
    my_loop.info_loop()
my_loop.end_loop()
