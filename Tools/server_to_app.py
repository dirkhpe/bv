"""
This script gets a list of (OOS/EOSL) servers and checks if there are connections to applications.

"""

import logging
import os
import pandas
from lib import my_env
from lib import neostore

# Node Labels
serverlbl = "Server"
# Relations


cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
soft_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["server2check"])
df = pandas.read_excel(soft_file)
# Get servers
servers = df.server.unique()
# Get known servers
server_nodes = ns.get_nodes(serverlbl)
server_d = {}
for sn in server_nodes:
    server_d[sn["hostName"]] = sn
query = """
    MATCH (server:Server)-[r:serverInst]->(inst:Instance)<-[:toInstance]-(solInstComp)
    WHERE server.hostName = '{host}'
    RETURN count(r) as rel_cnt
"""
# Check if all servers are known
for server in servers:
    try:
        sn = server_d[server]
    except KeyError:
        logging.error("Server {s} not in Murcs".format(s=server))
    else:
        q = query.format(host=server)
        cursor = ns.get_query(q)
        res = cursor.next()
        if res["rel_cnt"] > 0:
            logging.error("{s}: {c} relations".format(s=server, c=res["rel_cnt"]))
# Check OOS servers already OOS?
# Get servers in "tst-LLXGBS"
query = 'match (n:Server {systemLocation:"tst-LLXGBS", inScope:"Yes"}) return n'
tst_a = []
cursor = ns.get_query(query)
while cursor.forward():
    rec = cursor.current()["n"]
    tst_a.append(rec["hostName"])
cnt = 0
for row in df.iterrows():
    xl = row[1].to_dict()
    scope = xl["status"]
    server = xl["server"]
    if pandas.notnull(scope):
        if scope == "OOS":
            logging.info("Server {s} - Scope: {sc} - systemLocation: {sl}".format(s=server,
                                                                                  sc=server_d[server]["inScope"],
                                                                                  sl=server_d[server]["systemLocation"]))
            if server_d[server]["systemLocation"] == "tst-LLXGBS":
                try:
                    tst_a.remove(server)
                except ValueError:
                    logging.error("Trying to remove server {s}, but not in list.".format(s=server))
logging.info("Remaining servers: {a}".format(a=tst_a))
