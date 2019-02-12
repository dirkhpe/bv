"""
This script extracts Server information from Neo4J and converts it into files for import in Archi.
"""
import csv
import logging
import os
from lib import my_env
from lib import neostore
from lib.neostructure import *

ignore_props = ["cmdbSystemId", "dataQuality", "id", "murcsScope", "insideDMZ", "serverId", "nid"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)

el_list = []
prop_list = []
rel_list = []


def handle_nodes(nodes, name, archi):
    """
    This method handles a list of nodes. Name attribute has the node property for the name. Type is the Archimate type.
    Node properties that are not in the ignore list will be added as properties to the Archimate element.

    :param nodes: List of nodes that need to be handled.
    :param name: node attribute that will serve as the name.
    :param archi: Archimate type for the node.
    :return:
    """
    for node in nodes:
        node_dict = dict(node)
        el = dict(
            ID=node_dict["nid"],
            Type=archi,
            Name=node_dict[name]
            # Documentation="Node imported from MURCS."
        )
        el_list.append(el)
        props = [k for k in node_dict if k not in ignore_props]
        props.sort()
        for k in props:
            prop = dict(
                ID=node_dict["nid"],
                Key=k,
                Value=node_dict[k]
            )
            prop_list.append(prop)
    return


def handle_relations(cur, archi="AssociationRelationship"):
    """
    This method handles node relations. The cursor is the result of a query. Return values of the query are from_node
    and to_node.

    :param cur:
    :param archi: Relation type, default 'AssociationRelationship'
    :return:
    """
    while cur.forward():
        rec = cur.current
        from_node = rec["from_node"]
        to_node = rec["to_node"]
        from_id = from_node["nid"]
        to_id = to_node["nid"]
        rel = dict(
            ID="{hi}_{gi}".format(hi=from_id, gi=to_id),
            Type=archi,
            # Name="",
            # Documentation="",
            Source=from_id,
            Target=to_id
        )
        rel_list.append(rel)
    return


# Remove link between VPC Servers and site
# query = "MATCH (site:Site)-[rel:hasDev]->(srv:Server) WHERE srv.hostName CONTAINS 'VPC' DELETE rel"
# ns.get_query(query)

# Get sites
sites = ns.get_nodes(lbl_site)
handle_nodes(sites, name="dataCenterName", archi="Facility")

# Get physical servers
# Not every physical server has a location. A physical server never has incoming 'hasVirtual'.
query = """
        MATCH (server:{lbl_srv}) 
        WHERE NOT EXISTS ((:{lbl_srv})-[:{srv2srv}]->(server)) 
        AND NOT (server.hostName contains 'VPC') 
        RETURN server
        """.format(lbl_srv=lbl_server, srv2srv=site2server)
logging.info(query)
server_list = ns.get_query_data(query)
servers = [srv["server"] for srv in server_list]
handle_nodes(servers, name="hostName", archi="Device")

# Get virtual servers
# A virtual server must have an incoming 'hasVirtual'.
query = "MATCH (:{lbl_srv})-[:{srv2srv}]->(server:{lbl_srv}) RETURN server".format(lbl_srv=lbl_server,
                                                                                   srv2srv=server2server)
logging.info(query)
server_list = ns.get_query_data(query)
servers = [srv["server"] for srv in server_list]
handle_nodes(servers, name="hostName", archi="Node")

# Collect VPC servers
query = "MATCH (server:{node_lbl}) WHERE server.hostName contains 'VPC' RETURN server".format(node_lbl=lbl_server)
logging.info(query)
server_list = ns.get_query_data(query)
servers = [srv["server"] for srv in server_list]
handle_nodes(servers, name="hostName", archi="Node")

# Get Instances for System Software
instances = ns.get_nodes(lbl_instance)
handle_nodes(instances, name="instId", archi="SystemSoftware")

# Get Solution Components
solcomps = ns.get_nodes(lbl_solcomp)
handle_nodes(solcomps, name="solInstName", archi="TechnologyService")

# Get Solutions
# Todo: one solution has no properties - investigate!
query = "match (n:Solution) where not exists (n.solName) detach delete n"
ns.get_query(query)
solutions = ns.get_nodes(lbl_solution)
handle_nodes(solutions, name="solName", archi="ApplicationService")

# Get Relations
# Server to Server
query = "match (from_node:{lbl})-[:{rel}]->(to_node:{lbl}) return from_node, to_node".format(lbl=lbl_server,
                                                                                             rel=server2server)
logging.info(query)
cursor = ns.get_query(query)
handle_relations(cursor)

# Site to Server
query = "MATCH (from_node:{lbl_site})-[:{rel}]->(to_node:{lbl_srv}) return from_node, to_node"\
    .format(lbl_site=lbl_site, rel=site2server, lbl_srv=lbl_server)
logging.info(query)
cursor = ns.get_query(query)
handle_relations(cursor)

# Server to Instance
query = "MATCH (from_node:{from_lbl})-[:{rel_lbl}]->(to_node:{to_lbl}) RETURN from_node, to_node"\
    .format(from_lbl=lbl_server, to_lbl=lbl_instance, rel_lbl=server2instance)
logging.info(query)
cursor = ns.get_query(query)
handle_relations(cursor)

# Instance to Solution Component
query = """
        MATCH (from_node:{from_lbl})-[:{rel1}]->(:{ib_lbl})-[:{rel2}]->(to_node:{to_lbl}) 
        RETURN from_node, to_node
        """.format(from_lbl=lbl_instance, to_lbl=lbl_solcomp, ib_lbl=lbl_solinstcomp,
                   rel1=instance2solinstcomp, rel2=solinstcomp2solcomp)
logging.info(query)
cursor = ns.get_query(query)
handle_relations(cursor)

# SolComp to Solution
query = "MATCH (from_node:{from_lbl})-[:{rel_lbl}]->(to_node:{to_lbl}) RETURN from_node, to_node"\
    .format(from_lbl=lbl_solcomp, to_lbl=lbl_solution, rel_lbl=solcomp2solution)
logging.info(query)
cursor = ns.get_query(query)
handle_relations(cursor)

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
