"""
This script consolidates the murcs specific functions.
"""

excludedprops = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "clientId", "version", "dataQuality",
                 "ragState"]
srv_excluded = excludedprops + ["operatingSystem", "operatingSystemVersion"]
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

disc_sw = []    # List of softwareIds that have been discovered.


def fmo_hostName(fqdn):
    """
    This method will return the FMO hostName.

    :param fqdn: or servername.
    :return: servername.lower()
    """
    fqdn_arr = fqdn.strip().lower().split(".")
    return "{h}".format(h=fqdn_arr[0])


def fmo_serverId(fqdn):
    """
    This method will return the FMO serverId. FMO serverId has 'vpc.' in front of servername.

    :param fqdn: or servername.
    :return: 'vpc.' + servername.lower()
    """
    hostName = fmo_hostName(fqdn)
    serverId = "vpc.{h}".format(h=hostName)
    return serverId


def handle_properties(propdict):
    """
    This method handles the property information. In case of servers and solutions, properties are provided in a list of
    property dictionaries. In case of solution instances, properties are provided as a dictionary with the property
    name is key and attributes are in the value dictionary.

    :param propdict: list or dictionary.
    :return:
    """
    # Convert dictionary to list
    if isinstance(propdict, dict):
        propdict = [propdict[k] for k in propdict if 'imagePositions' not in k]
    if len(propdict) > 0:
        for cnt in range(len(propdict)):
            try:
                propdict[cnt].pop("self")
            except KeyError:
                pass
    return propdict


def handle_person(persondict):
    if isinstance(persondict, dict):
        return persondict["email"]
    else:
        return None


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
        softwareId = swdict["softwareId"]
        if softwareId in disc_sw:
            return softwareId, None
        else:
            disc_sw.append(softwareId)
            swdict["status"] = None
            return softwareId, swdict
    else:
        return None


def handle_solution(soldict):
    if isinstance(soldict, dict):
        return str(soldict["solutionId"])
    else:
        return None


def handle_solutionInstance(solinstdict, solId):
    solInstComp_res = []
    solInstProps = []
    if len(solinstdict) > 0:
        for cnt in range(len(solinstdict)):
            solinstdict[cnt]["solutionId"] = handle_solution(solinstdict[cnt].pop("solution"))
            solinstdict[cnt].pop("contactPersons")
            # Handle solution Instance Component records.
            solinstcomp = solinstdict[cnt].pop("solutionInstanceComponents")
            if len(solinstcomp) > 0:
                handle_solinstcomp(solinstcomp, solId, solinstdict[cnt]["solutionInstanceId"])
                solInstComp_res += solinstcomp
            # Todo: handle solution instance components properties.
            solInstProps += handle_properties(solinstdict[cnt].pop("solutionInstanceProperties"))
    return solinstdict, solInstComp_res, solInstProps


def handle_solToSol(soltosoldict, solToSol_done):
    remember_res = []
    if len(soltosoldict) > 0:
        for cnt in range(len(soltosoldict)):
            solToSolId = soltosoldict[cnt]["solutionToSolutionId"]
            # Make sure to capture only first appearance of solToSolId
            if solToSolId not in solToSol_done:
                solToSol_done.append(solToSolId)
                soltosoldict[cnt]["fromSolutionId"] = handle_solution(soltosoldict[cnt].pop("fromSolution"))
                soltosoldict[cnt]["toSolutionId"] = handle_solution(soltosoldict[cnt].pop("toSolution"))
                # Todo: handle solutionToSolution Properties!
                soltosoldict[cnt].pop("solutionToSolutionProperties")
                remember_res.append(soltosoldict[cnt])
    return remember_res


def handle_swinstid(swinstdict):
    softwareInstanceId = swinstdict["softwareInstanceId"]
    softwareId = handle_software(swinstdict["software"])[0]
    serverId = handle_server(swinstdict["server"])
    return softwareInstanceId, softwareId, serverId


def handle_solinstcomp(solinstcompdict, solutionId, solutionInstanceId):
    for cnt in range(len(solinstcompdict)):
        softwareInstanceId, softwareId, serverId = handle_swinstid(solinstcompdict[cnt].pop("softwareInstance"))
        solinstcompdict[cnt]["softwareInstanceId"] = softwareInstanceId
        solinstcompdict[cnt]["softwareId"] = softwareId
        solinstcompdict[cnt]["serverId"] = serverId
        solinstcompdict[cnt]["solutionId"] = solutionId
        solinstcompdict[cnt]["solutionInstanceId"] = solutionInstanceId
        # Todo: process State variable
        solinstcompdict[cnt]["status"] = None
    return solinstcompdict
