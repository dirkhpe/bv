"""
This script will collect information from Murcs and store it in a local database.

This is the original version of murcs_Get.py script. It looks like optimization in Solution collection is possible by
evaluating solution details.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest


cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)

"""
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

logging.info("Handling Server detail information")
query = "SELECT serverId FROM server"
records = lcl.get_query(query)
my_loop = my_env.LoopInfo("Servers for Network Information", 20)
for record in records:
    my_loop.info_loop()
    serverId = record["serverId"]
    res = r.get_server(serverId)
    netinfo = res["serverNetworkInterfaces"]
    if len(netinfo) > 0:
        for cnt in range(len(netinfo)):
            netinfo[cnt]["serverId"] = serverId
            ipaddress_list = netinfo[cnt].pop("serverNetworkInterfaceIPAddresses")
            if len(ipaddress_list) > 0:
                lcl.insert_rows("ipaddress", ipaddress_list)
        lcl.insert_rows("netiface", netinfo)
    contacts = res["contactPersons"]
    if len(contacts) > 0:
        for cnt in range(len(contacts)):
            contacts[cnt]["email"] = handle_person(contacts[cnt].pop("person"))
        lcl.insert_rows("contactserver", contacts)

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
"""

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
            # Handle solution Instance Component records.
            solinstcomp = res[cnt].pop("solutionInstanceComponents")
            handle_solinstcomp(solId, res[cnt]["solutionInstanceId"], solinstcomp)
            if len(solinstcomp) > 0:
                lcl.insert_rows("solinstcomp", solinstcomp)
            # Todo: handle solution instance components properties.
            res[cnt].pop("solutionInstanceProperties")
        lcl.insert_rows("solinst", res)
my_loop.end_loop()

logging.info("Handling solution to solution instances")
solToSol_done = []
query = "SELECT solutionId FROM solution"
records = lcl.get_query(query)
my_loop = my_env.LoopInfo("Solutions for Solution Instances", 20)
for record in records:
    my_loop.info_loop()
    solId = record["solutionId"]
    res = r.get_soltosol_from_solution(solId)
    if len(res) > 0:
        remember_res = []
        for cnt in range(len(res)):
            solToSolId = res[cnt]["solutionToSolutionId"]
            # Make sure to capture only first appearance of solToSolId
            if solToSolId not in solToSol_done:
                solToSol_done.append(solToSolId)
                res[cnt]["fromSolutionId"] = handle_solution(res[cnt].pop("fromSolution"))
                res[cnt]["toSolutionId"] = handle_solution(res[cnt].pop("toSolution"))
                # Todo: handle solutionToSolution Properties!
                res[cnt].pop("solutionToSolutionProperties")
                remember_res.append(res[cnt])
            else:
                print("{sts} already handled".format(sts=solToSolId))
        if len(remember_res) > 0:
            lcl.insert_rows("soltosol", remember_res)
my_loop.end_loop()

"""
logging.info("Handling Person information")
res = []
r.get_data("persons", reslist=res)
lcl.insert_rows("person", res)
"""
