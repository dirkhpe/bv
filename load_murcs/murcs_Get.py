"""
This script will collect information from Murcs and store it in a local database.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

solToSol_done = []


cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)

logging.info("Get Version Information")
res = r.get_version()
lcl.insert_row("version", res)

res = []
logging.info("Get Site information")
r.get_data("sites", reslist=res)
lcl.insert_rows("site", res)

logging.info("Handling Person information")
res = []
r.get_data("persons", reslist=res)
lcl.insert_rows("person", res)

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
my_loop = my_env.LoopInfo("Server Details", 20)
for record in records:
    my_loop.info_loop()
    serverId = record["serverId"]
    res = r.get_server(serverId)
    netinfo = res.pop("serverNetworkInterfaces")
    if len(netinfo) > 0:
        for cnt in range(len(netinfo)):
            netinfo[cnt]["serverId"] = serverId
            ipaddress_list = netinfo[cnt].pop("serverNetworkInterfaceIPAddresses")
            if len(ipaddress_list) > 0:
                lcl.insert_rows("ipaddress", ipaddress_list)
        lcl.insert_rows("netiface", netinfo)
    contacts = res.pop("contactPersons")
    if len(contacts) > 0:
        for cnt in range(len(contacts)):
            contacts[cnt]["email"] = handle_person(contacts[cnt].pop("person"))
        lcl.insert_rows("contactserver", contacts)
    serverproperties = handle_properties(res.pop("serverProperties"))
    lcl.insert_rows("serverproperty", serverproperties)
    softinstances = res.pop("softwareInstances")
    if len(softinstances) > 0:
        for cnt in range(len(softinstances)):
            softinstances[cnt]["serverId"] = handle_server(softinstances[cnt].pop("server"))
            softinstances[cnt]["softwareId"], swdict = handle_software(softinstances[cnt].pop("software"))
            if isinstance(swdict, dict):
                lcl.insert_row("software", swdict)
        lcl.insert_rows("softinst", softinstances)

logging.info("Collecting Solutions")
res = []
r.get_data("solutions", reslist=res)
for cnt in range(len(res)):
    # Todo: process State variable
    res[cnt]["status"] = None
lcl.insert_rows("solution", res)

logging.info("Handling Solutions")
query = "SELECT solutionId FROM solution"
records = lcl.get_query(query)
my_loop = my_env.LoopInfo("Solutions", 20)
for record in records:
    my_loop.info_loop()
    solId = record["solutionId"]
    res = r.get_solution(solId)
    if len(res) > 0:
        solutionId = res.pop("solutionId")
        solToSol_res = handle_solToSol(res.pop("toSolution"), solToSol_done)
        lcl.insert_rows("soltosol", solToSol_res)
        solToSol_res = handle_solToSol(res.pop("fromSolution"), solToSol_done)
        lcl.insert_rows("soltosol", solToSol_res)
        solInstance_res, solInstComp_res, solInstProps = handle_solutionInstance(res.pop("solutionInstances"),
                                                                                 solutionId)
        lcl.insert_rows("solinst", solInstance_res)
        lcl.insert_rows("solinstcomp", solInstComp_res)
        lcl.insert_rows("solinstproperty", solInstProps)
        contacts = res["contactPersons"]
        if len(contacts) > 0:
            for cnt in range(len(contacts)):
                contacts[cnt]["email"] = handle_person(contacts[cnt].pop("person"))
            lcl.insert_rows("contactsolution", contacts)
        solprops = handle_properties(res.pop("solutionProperties"))
        lcl.insert_rows("solutionproperty", solprops)
my_loop.end_loop()

logging.info("End Application")
