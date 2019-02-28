"""
This script consolidates the murcs specific functions.
"""

server_ignore = ["id", "changedAt", "changedBy", "createdAt", "createdBy",
                 "clientId", "siteId", "version", "dataQuality", "parentServerId"]
solcomp_ignore = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "version", "solId"]
excludedprops = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "clientId", "version", "dataQuality",
                 "ragState"]

fixedprops = dict(
    murcsScope="Full"
)
"""
prop2dict translates attribute to dictionary item in payload. Attribute is key. Name of dictionary item is first item in
tuple, name of the key is second item in dictionary key. 
"""
srv_prop2dict = dict(
    siteId=("site", "siteId"),
    parentServer=("parentServer", "serverId")
)
softInst_prop2dict = dict(
    serverId=("server", "serverId"),
    softwareId=("software", "softwareId")
)
solInst_prop2dict = dict(
    solutionId=("solution", "solutionId")
)


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


def handle_solinstcomp(solutionId, solutionInstanceId, res):
    for cnt in range(len(res)):
        softwareInstanceId, softwareId, serverId = handle_swinstid(res[cnt].pop("softwareInstance"))
        res[cnt]["softwareInstanceId"] = softwareInstanceId
        res[cnt]["softwareId"] = softwareId
        res[cnt]["serverId"] = serverId
        res[cnt]["solutionId"] = solutionId
        res[cnt]["solutionInstanceId"] = solutionInstanceId
        # Todo: process State variable
        res[cnt]["status"] = None
