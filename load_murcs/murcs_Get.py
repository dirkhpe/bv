"""
This script will collect information from Murcs and store it in a local database.
"""
import logging
from lib import localstore
from lib import my_env
from lib import murcsrest


def handle_server(serverdict):
    if isinstance(serverdict, dict):
        return serverdict["serverId"]
    else:
        return None


def handle_site(sitedict):
    if isinstance(sitedict, dict):
        return sitedict["siteId"]
    else:
        return None


def handle_software(swdict):
    if isinstance(swdict, dict):
        return swdict["softwareId"]
    else:
        return None


def handle_solution(soldict):
    if isinstance(soldict, dict):
        return str(soldict["solutionId"])
    else:
        return None


def handle_swinstid(swinstdict):
    softwareInstanceId = swinstdict["softwareInstanceId"]
    softwareId = handle_software(swinstdict["software"])
    serverId = handle_server(swinstdict["server"])
    return softwareInstanceId, softwareId, serverId


def handle_solinstcomp(solutionId, solutionInstanceId, result):
    for cntr in range(len(result)):
        softwareInstanceId, softwareId, serverId = handle_swinstid(res[cnt].pop("softwareInstance"))
        res[cntr]["softwareInstanceId"] = softwareInstanceId
        res[cntr]["softwareId"] = softwareId
        res[cntr]["serverId"] = serverId
        res[cntr]["solutionId"] = solutionId
        res[cntr]["solutionInstanceId"] = solutionInstanceId
        # Todo: process State variable
        res[cnt]["status"] = None
    lcl.insert_rows("solinstcomp", res)


cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)

res = []
r.get_data("sites", reslist=res)
lcl.insert_rows("site", res)

logging.info("Handling Servers")
res = []
r.get_data("servers", reslist=res)
for cnt in range(len(res)):
    res[cnt]["parentServer"] = handle_server(res[cnt]["parentServer"])
    res[cnt]["siteId"] = handle_site(res[cnt].pop("site"))
    # Todo: process State variable
    res[cnt]["status"] = None
lcl.insert_rows("server", res)

logging.info("Handling Software")
res = []
r.get_data("software", reslist=res)
for cnt in range(len(res)):
    # Todo: process State variable
    res[cnt]["status"] = None
lcl.insert_rows("software", res)

logging.info("Handling Software Instances")
query = "SELECT serverId FROM server"
records = lcl.get_query(query)
my_loop = my_env.LoopInfo("Server for Software Instances", 20)
for record in records:
    my_loop.info_loop()
    serverId = record["serverId"]
    res = r.get_softinst_from_server(serverId)
    if len(res) > 0:
        for cnt in range(len(res)):
            res[cnt]["serverId"] = handle_server(res[cnt].pop("server"))
            res[cnt]["softwareId"] = handle_software(res[cnt].pop("software"))
        lcl.insert_rows("softinst", res)
my_loop.end_loop()

logging.info("Handling Solutions")
res = []
r.get_data("solutions", reslist=res)
for cnt in range(len(res)):
    # Todo: process State variable
    res[cnt]["status"] = None
lcl.insert_rows("solution", res)

logging.info("Handling Solution Instances")
query = "SELECT solutionId FROM solution"
records = lcl.get_query(query)
my_loop = my_env.LoopInfo("Solutions for Solution Instances", 20)
for record in records:
    my_loop.info_loop()
    solId = record["solutionId"]
    res = r.get_solinst_from_solution(solId)
    if len(res) > 0:
        for cnt in range(len(res)):
            res[cnt]["solutionId"] = handle_solution(res[cnt].pop("solution"))
            res[cnt].pop("contactPersons")
            handle_solinstcomp(solId, res[cnt]["solutionInstanceId"], res[cnt].pop("solutionInstanceComponents"))
            res[cnt].pop("solutionInstanceProperties")
        lcl.insert_rows("solinst", res)
my_loop.end_loop()
