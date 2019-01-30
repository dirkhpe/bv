"""
This script extracts Server information from Neo4J and converts it into files for import in Archi.
"""
import csv
import logging
import os
from lib import my_env
from lib import neostore
from lib.neostructure import *

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)

el_list = []
prop_list = []
# Get servers
servers = ns.get_nodes(lbl_server)
for server in servers:
    server_dict = dict(server)
    el = dict(
        ID=server_dict["id"],
        Type="Node",
        Name=server_dict["hostName"],
        Documentation="Server imported from MURCS."
    )
    el_list.append(el)
    props = [k for k in server_dict if k not in ignore_server]
    props.sort()
    for k in props:
        prop = dict(
            ID=server_dict["id"],
            Key=k,
            Value=server_dict[k]
        )
        prop_list.append(prop)

# Get Relations
rel_list = []
query = "match (host:{lbl})-[{rel}]->(guest:{lbl}) return host, guest".format(lbl=lbl_server, rel=server2server)
cursor = ns.get_query(query)
while cursor.forward():
    rec = cursor.current()
    host = rec["host"]
    guest = rec["guest"]
    host_id = host["id"]
    guest_id = guest["id"]
    rel = dict(
        ID="{hi}_{gi}".format(hi=host_id, gi=guest_id),
        Type="AssociationRelationship",
        Name="",
        Documentation="",
        Source=host_id,
        Target=guest_id
    )
    rel_list.append(rel)


csv.register_dialect('this_app_dialect', delimiter=',', quoting=csv.QUOTE_ALL)
# write elements
elcols = ["ID", "Type", "Name", "Documentation"]
fn = os.path.join(cfg["Archi"]["dir"], "murcs-elements.csv")
with open(fn, "w", newline="", encoding="utf-8") as elfile:
    writer = csv.DictWriter(elfile, fieldnames=elcols, dialect='this_app_dialect')
    writer.writeheader()
    for line in el_list:
        writer.writerow(line)

# write properties
propcols = ["ID", "Key", "Value"]
fn = os.path.join(cfg["Archi"]["dir"], "murcs-properties.csv")
with open(fn, "w", newline="", encoding="utf-8") as propfile:
    writer = csv.DictWriter(propfile, fieldnames=propcols, dialect='this_app_dialect')
    writer.writeheader()
    for line in prop_list:
        writer.writerow(line)

# write relations
relcols = ["ID", "Type", "Name", "Documentation", "Source", "Target"]
fn = os.path.join(cfg["Archi"]["dir"], "murcs-relations.csv")
with open(fn, "w", newline="", encoding="utf-8") as relfile:
    writer = csv.DictWriter(relfile, fieldnames=relcols, dialect='this_app_dialect')
    writer.writeheader()
    for line in rel_list:
        writer.writerow(line)
