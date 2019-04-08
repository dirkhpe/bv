"""
This module consolidates the Murcs Rest Calls
"""
import logging
import os
import requests
import json
from lib import my_env


class MurcsRest:
    """
    This class will set up the attributes for the Murcs Rest call.
    """

    def __init__(self, cfg):
        """
        The init procedure will set-up the Murcs Rest parameters.

        :param cfg: Link to the configuration object.
        """
        # Remove http_proxy environment settings if they exist.
        # If they exist, Python "requests" module will route over http_proxy instead of using OpenVPN.
        try:
            os.environ.pop("http_proxy")
            os.environ.pop("https_proxy")
        except KeyError:
            pass
        self.user = os.getenv("MURCS_USER")
        self.passwd = os.getenv("MURCS_PWD")
        host = os.getenv("MURCS_HOST")
        port = os.getenv("MURCS_PORT")
        clientId = os.getenv("MURCS_CLIENTID")
        self.url_base = "http://{host}:{port}/murcs/rest/{clientId}/".format(host=host,
                                                                             port=port,
                                                                             clientId=clientId)

    def add_server(self, serverId, payload):
        """
        This method will load a server in Murcs.

        :param serverId: serverId to load
        :param payload: Dictionary with properties to load
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "servers/{serverId}".format(serverId=serverId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load server {serverId}!".format(serverId=serverId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_server_contact(self, serverId, personId, role):
        """
        This method will add a Person to a server in a role.

        :param serverId: ID of the server
        :param personId: email of to the Person.
        :param role: Role of the person
        :return:
        """
        path = "servers/{serverId}/contactPersons/{personId}/{role}".format(serverId=serverId, personId=personId,
                                                                            role=role)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Contact {personId} added to server {serverId}!".format(serverId=serverId,
                                                                                 personId=personId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_server_property(self, serverId, payload):
        """
        This method will add a property to a server.

        :param serverId:
        :param payload: Dictionary with propertyName, propertyValue and description
        :return:
        """
        propname = payload["propertyName"]
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "servers/{serverId}/properties/{prop}".format(serverId=serverId, prop=propname)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Property {prop} with value {val} added to server {serverId}!"
                         .format(prop=propname, serverId=serverId, val=payload["propertyValue"]))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_site(self, siteId, payload):
        """
        This method will load a site in Murcs.

        :param siteId: siteId to load
        :param payload: Dictionary with properties to load
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "sites/{siteId}".format(siteId=siteId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load site {siteId}!".format(siteId=siteId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_sol(self, solId, payload):
        """
        This method will load a solution in Murcs.

        :param solId: solId to load
        :param payload: Dictionary with properties to load
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "solutions/{solId}".format(solId=solId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load solution {solId}!".format(solId=solId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def get_data(self, objtype, start=0, limit=100, reslist=None):
        """
        This method launches the Rest call to get the murcs data for a specific object type (site, servers, ...)

        :param objtype: Object type for which Murcs information is collected.
        :param start: Offset of the return set, default 0
        :param limit: Number of lines in the return set, default 100
        :param reslist:
        :return: Murcs information as a parsed json string.
        """
        logging.debug("Start: {start}, limit: {limit}".format(start=start, limit=limit))
        url = self.url_base + objtype
        headers = {
            'Accept': 'application/json'
        }
        payload = dict(
            start=start,
            limit=limit
        )
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd), params=payload)
        if r.status_code == 200:
            res = r.json()
            reslist += res["items"]
            totalResults = res["totalResults"]
            nextStart = start + limit
            if nextStart < totalResults:
                self.get_data(objtype, nextStart, limit, reslist)
            else:
                return
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
            return

    def get_server(self, serverId):
        """
        This method launches the Rest call to get the server information for a single server. This method is used to
        collect network interface and IP information.

        :param serverId: Server Id required.
        :return: Murcs information as a parsed json string.
        """
        url = self.url_base + 'servers/{serverId}'.format(serverId=serverId)
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            res = r.json()
            return res
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
            return

    def get_softinst_from_server(self, serverId):
        """
        This method launches the Rest call to get the software Instances for a server. Limit is set to 100. No server
        should have more than 100 server instances.

        :param serverId: Server Id for which the software Instances are required.
        :return: Murcs information as a parsed json string.
        """
        limit = 100
        url = self.url_base + 'servers/{serverId}/softwareInstances'.format(serverId=serverId)
        headers = {
            'Accept': 'application/json'
        }
        payload = dict(
            limit=limit
        )
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd), params=payload)
        if r.status_code == 200:
            res = r.json()
            return res
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
            return

    def get_solution(self, solutionId):
        """
        This method launches the Rest call to get the solution information

        :param solutionId:
        :return:
        """
        url = self.url_base + 'solutions/{solutionId}'.format(solutionId=solutionId)
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            res = r.json()
            return res
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
            return

    def get_solinst_from_solution(self, solId):
        """
        This method launches the Rest call to get the solution Instances for a solution. This needs to be done in two
        steps. 1. Find the solutionInstance Ids attached to this solution. 2. Find the details for every solution
        Instance Id.

        :param solId: Solution Id for which the solution Instances are required.
        :return: Murcs information as a parsed json string.
        """
        limit = 100
        url = self.url_base + 'solutions/{solId}/solutionInstances'.format(solId=solId)
        headers = {
            'Accept': 'application/json'
        }
        payload = dict(
            limit=limit
        )
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd), params=payload)
        if r.status_code == 200:
            res = r.json()
            solInstRecs = []
            for rec in res:
                solInstId = rec["key"]
                solInstDict = self.get_solinst_details_from_solution(solId, solInstId)
                if isinstance(solInstDict, dict):
                    solInstRecs.append(solInstDict)
            return solInstRecs
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
            return

    def get_solinst_details_from_solution(self, solId, solInstId):
        """
        This method launches the Rest call to get the solution Instances details for a solution. This is the second step
        after calling get_solinst_from_solution. In this step solution Instance Components are also collected.

        :param solId: Solution Id for which the solution Instances are required.
        :param solInstId: Solution Instance Id for which the details are required.
        :return: Murcs information as a parsed json string.
        """
        limit = 100
        url = self.url_base + 'solutions/{solId}/solutionInstances/{solInstId}'.format(solId=solId, solInstId=solInstId)
        headers = {
            'Accept': 'application/json'
        }
        payload = dict(
            limit=limit
        )
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd), params=payload)
        if r.status_code == 200:
            res = r.json()
            return res
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
            return

    def get_soltosol_from_solution(self, solId):
        """
        This method launches the Rest call to get the solution to solution details for a solution.

        :param solId: Solution Id for which the solution to solution Instances are required.
        :return: Murcs information as a parsed json string.
        """
        limit = 100
        url = self.url_base + 'solutionToSolution/all/{solId}'.format(solId=solId)
        headers = {
            'Accept': 'application/json'
        }
        payload = dict(
            limit=limit
        )
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd), params=payload)
        if r.status_code == 200:
            res = r.json()
            return res["items"]
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
            return

    def get_wave(self, solId):
        """
        This method launches the Rest call to get wave information

        :param solId: Solution ID for which wave info is required.
        :return:
        """
        url = self.url_base + 'solutions/{solId}'.format(solId=solId)
        headers = {
            'Accept': 'application/json'
        }
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            parsed_json = r.json()
            print(parsed_json['fromSolution'][0]['comment'])
        else:
            print("Investigate: {s}".format(s=r.status_code))
            print(r.content)
            r.raise_for_status()
        return

    def add_person(self, email, payload):
        """
        This method will add a Person to the system.

        :param email: unique identifier for Person
        :param payload: Payload to be added to the Person.
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "persons/{email}".format(email=email)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load person {email}!".format(email=email))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_serverNetIface(self, serverId, ifaceId, payload=None):
        """
        This method will add a Network Interface to a server.

        :param serverId: unique server Id
        :param ifaceId: Network Interface ID.
        :param payload: Payload to be added. serverId and ifaceId must be included in the payload.
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "{serverId}/serverNetworkInterfaces/{ifaceId}".format(serverId=serverId, ifaceId=ifaceId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load Network Interface {ifaceId}!".format(ifaceId=ifaceId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_serverNetIfaceIp(self, serverId, ifaceId, ipAddress, payload=None):
        """
        This method will add a Network Interface to a server.

        :param serverId: unique server Id
        :param ifaceId: Network Interface ID
        :param ipAddress: IP Address to be added.
        :param payload: Payload to be added.
        :return:
        """
        if not payload:
            payload = {}
        payload["networkInterfaceId"] = ifaceId
        payload["ipAddress"] = ipAddress
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "{serverId}/serverNetworkInterfaces/{ifaceId}/serverNetworkInterfacesIpAddress/{ipAddress}"\
            .format(serverId=serverId, ifaceId=ifaceId, ipAddress=ipAddress)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load IP {ipAddress} to Network Interface {ifaceId}!".format(ifaceId=ifaceId,
                                                                                      ipAddress=ipAddress))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_soft(self, softId, payload):
        """
        This method will add a Software to the system.

        :param softId: unique software Id
        :param payload: Payload to be added.
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "software/{softId}".format(softId=softId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load soft {softId}!".format(softId=softId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_software_from_sol(self, sol_rec):
        """
        This method will create a Software from a Solution.

        :param sol_rec: Dictionary with keys solId and solName
        :return:
        """
        softId = "{solId} software".format(solId=sol_rec["solId"])
        softName = "{solName} (software)".format(solName=sol_rec["solName"])
        payload = dict(
            softwareId=softId,
            softwareName=softName,
            softwareType="Application",
            softwareSubType="Application Implementation",
            # softwareVersion="Production",
            inScope="Unknown"
        )
        data = json.dumps(payload)
        url = self.url_base + "software/{softId}".format(softId=softId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("software {softId} is created for solution {solId}!".format(solId=sol_rec["solId"],
                                                                                     softId=softId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_softInst(self, softInstId, payload):
        """
        This method will add a Software Instance to the system. For linking server with software, check function
        add_softInstCalc.

        :param softInstId: unique software Instance Id
        :param payload: Payload to be added.
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "softwareInstances/{softInstId}".format(softInstId=softInstId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load softwareInstance {softInstId}!".format(softInstId=softInstId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_softInst_calc(self, softId, serverId, **params):
        """
        This method will link a Software (from a solution) to a server by calculating parameters.
        By default the softInstId is "softId serverId". In case this is softInstance for Application, then
        environment will be added if it is other than 'Production'. Current environments are Production, Development
        and Quality. Environment is also in instSubType then.
        In case this is a database with a known schema, instSubType will have the schema name.

        :param softId: ID Name for the Software
        :param serverId: ID Name for the Server. If serverId starts with 'vpc.' then this will converted to 'VPC.'
        :param params: dictionary with additional attributes. softInstId is mandatory for Type 'Application' Type and
        environment not Production. instSubType: (Optional) Schema of the instance, or environment for Application-type
        software instances. instType: Defaults to 'Application'.
        :return:
        """
        params["server"] = dict(serverId=serverId)
        if 'vpc' == serverId[:len('vpc')]:
            serverId = 'VPC' + serverId[len('vpc'):]
        try:
            softwareInstanceId = params.pop("softInstId")
        except KeyError:
            # Check if instSubType (schema of the instance) is defined.
            try:
                instSubType = params.pop("instSubType")
            except KeyError:
                softwareInstanceId = "{softId} {serverId}".format(softId=softId, serverId=serverId)
            else:
                softwareInstanceId = "{schema} {softId} {serverId}".format(softId=softId, serverId=serverId,
                                                                           schema=instSubType)
                params["instanceSubType"] = instSubType
        try:
            softwareInstanceType = params.pop("instType")
        except KeyError:
            softwareInstanceType = "Application"
        params["software"] = dict(softwareId=softId)
        params["softwareInstanceId"] = softwareInstanceId
        params["softwareInstanceType"] = softwareInstanceType
        data = json.dumps(params)
        logging.debug("Payload: {p}".format(p=data))
        url = self.url_base + "softwareInstances/{softwareInstanceId}".format(softwareInstanceId=softwareInstanceId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("software Instance *{softInstId}* is created!".format(softInstId=softwareInstanceId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_softInst_property(self, inst_rec, payload):
        """
        This method will add a property to a software Instance.

        :param inst_rec: Software Instance record, containing instId, softId, serverID
        :param payload: Dictionary with propertyName, propertyValue and description
        :return:
        """
        instId = inst_rec["instId"]
        softId = inst_rec["softId"]
        serverId = inst_rec["serverId"]
        propname = payload["propertyName"]
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "softwareInstances/{serverId}/{softId}/{instId}/properties/{prop}"\
            .format(softId=softId, instId=instId, prop=propname, serverId=serverId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Property {prop} with value {val} added to softInst {instId}!"
                         .format(prop=propname, instId=instId, val=payload["propertyValue"]))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solComp_property(self, solcomp_rec, payload):
        """
        This method will add a property to a solution component.

        :param solcomp_rec:
        :param payload: Dictionary with propertyName, propertyValue and description
        :return:
        """
        solId = solcomp_rec["solId"]
        solInstId = solcomp_rec["solInstId"]
        propname = payload["propertyName"]
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "solutions/{solId}/solutionInstances/{solInstId}/properties/{prop}"\
            .format(solId=solId, solInstId=solInstId, prop=propname)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Property {prop} with value {val} added to solComp {solInstId}!"
                         .format(prop=propname, solInstId=solInstId, val=payload["propertyValue"]))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solInstComp(self, solInstId, softInstId, solId, serverId, softId, mode="CMO"):
        """
        This method will add a solutionInstanceComponent as the final link between solution and server.

        :param solInstId:
        :param softInstId:
        :param solId:
        :param serverId:
        :param softId:
        :param mode: CMO or FMO. If FMO, validFrom date will be set to '2300-01-01' and the connection will be created
        for FMO. CMO is default
        :return:
        """
        server = dict(serverId=serverId)
        software = dict(softwareId=softId)
        solution = dict(solutionId=solId)
        softwareInstance = dict(
            softwareInstanceId=softInstId,
            software=software,
            server=server
        )
        solutionInstance = dict(
            solutionInstanceId=solInstId,
            solution=solution
        )
        sIC = solInstId + " " + softInstId
        payload = dict(
            solSoftId=sIC,
            solutionInstance=solutionInstance,
            softwareInstance=softwareInstance
        )
        if mode == 'FMO':
            payload["validFrom"] = "2030-01-01T00:00:00Z"
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        url = self.url_base + 'solutionInstanceComponents'
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("solution Instance Component {sIC} is created!".format(sIC=sIC))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solInst(self, solId, solInstId, payload):
        """
        This method will add a Solution Instance to the system. Two other functions are available: add_solutionInstance
        and add_solutionComponent. These functions will calculate the payload from a limited number of input.
        It may be better to remove payload calculation from this library and keep only add_solInst.

        :param solId: solution Id to link solution Instance to.
        :param solInstId: unique solution Instance Id
        :param payload: Payload to be added.
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "solutions/{solId}/solutionInstances/{solInstId}".format(solId=solId, solInstId=solInstId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Load solution Instance {solInstId}!".format(solInstId=solInstId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solToSol(self, solToSolId, fromSolId, toSolId, payload):
        """
        This method will remove a solution to solution relation.

        :param solToSolId: ID of the solution to Solution Component
        :param fromSolId: ID of the Source Solution Component
        :param toSolId: ID of the Target Solution Component.
        :param payload: Payload for the PUT.
        :return:
        """
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        url = self.url_base + 'solutionToSolution/{fromSolId}/{toSolId}/{solToSolId}'.format(fromSolId=fromSolId,
                                                                                             toSolId=toSolId,
                                                                                             solToSolId=solToSolId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("solution to Solution {sIC} is added!".format(sIC=solToSolId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solutionComponent(self, sol_rec, env):
        """
        This method will add a solution Component to a solution. A solution component has an environment identifier.
        There can be multiple solution components attached to a solution.

        :param sol_rec: Solution Record.
        :param env: Environment (Production, Development, Quality)
        :return:
        """
        solId = sol_rec["solId"]
        solInstId = my_env.get_solInstId(solId, env)
        solution = dict(solutionId=solId)
        env_abbr = my_env.env2abbr(env)
        payload = dict(
            solutionInstanceId=solInstId,
            solutionInstanceName="{solName} ({env_abbr})".format(solName=sol_rec["solName"], env_abbr=env_abbr),
            solutionInstanceType="Application Instance",
            environment=env,
            solution=solution,
            comment='added by Python Script'
        )
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        url = self.url_base + 'solutions/{solId}/solutionInstances/{solInstId}'\
            .format(solId=solId, solInstId=solInstId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("solution Instance {solInstId} is created for solution {solId}!".format(solId=solId,
                                                                                                 solInstId=solInstId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solutionInstance(self, sol_rec):
        """
        This method will add a solution Instance to a solution.
        A solution instance is a special kind of solution Component. A solution instance is used if there is only one
        required. If more than one objects are required (e.g. Production, Development, Quality, ...) then a Solution
        Component need to be used. Default solution instance is in environment Production.

        :param sol_rec: Solution Record.
        :return:
        """
        solId = sol_rec["solId"]
        solInstId = "{solId} solInstance".format(solId=solId)
        solution = dict(solutionId=solId)
        payload = dict(
            solutionInstanceId=solInstId,
            solutionInstanceName="{solName} (inst)".format(solName=sol_rec["solName"]),
            solutionInstanceType="Application Instance",
            environment='Production',
            solution=solution,
            comment='added by Python Script'
        )
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        url = self.url_base + 'solutions/{solId}/solutionInstances/{solInstId}'\
            .format(solId=solId, solInstId=solInstId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("solution Instance {solInstId} is created for solution {solId}!".format(solId=solId,
                                                                                                 solInstId=solInstId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solution_contact(self, solId, personId, role):
        """
        This method will add a Person to a solution in a role.

        :param solId: ID of the solution
        :param personId: email of to the Person.
        :param role: Role of the person
        :return:
        """
        path = "solutions/{solId}/contactPersons/{personId}/{role}".format(solId=solId, personId=personId, role=role)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Contact {personId} added to solution {solId}!".format(solId=solId, personId=personId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def add_solution_property(self, solId, payload):
        """
        This method will add a property to a solution.

        :param solId: Solution ID
        :param payload: Dictionary with propertyName, propertyValue and description
        :return:
        """
        propname = payload["propertyName"]
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        path = "solutions/{solId}/properties/{prop}".format(solId=solId, prop=propname)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Property {prop} with value {val} added to solution {solId}!"
                         .format(prop=propname, solId=solId, val=payload["propertyValue"]))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def get_softInst_property(self, inst_rec, propname):
        """
        This method will add a property to a software Instance.

        :param inst_rec: Software Instance record, containing instId, softId, serverID
        :param propname: propertyName
        :return:
        """
        instId = inst_rec["instId"]
        softId = inst_rec["softId"]
        serverId = inst_rec["serverId"]
        path = "softwareInstances/{serverId}/{softId}/{instId}/properties/{prop}"\
            .format(softId=softId, instId=instId, prop=propname, serverId=serverId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.get(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            return r.json()
            # logging.info("Property {prop} with value {val} added to softInst {instId}!"
            #              .format(prop=propname, instId=instId, val=payload["propertyValue"]))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_person(self, email):
        """
        This method will remove a Person.

        :param email: ID (email) of the person to be removed
        :return:
        """
        path = "persons/{email}".format(email=email)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Contact {personId} removed!".format(personId=email))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_server(self, serverId):
        """
        This method will remove a server in Murcs.

        :param serverId: serverId to remove
        :return:
        """
        path = "servers/{serverId}".format(serverId=serverId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Remove server {serverId}!".format(serverId=serverId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_server_property(self, serverId, prop):
        """
        This method will delete a property from a server.

        :param serverId: Id of the server
        :param prop: property name of the server
        :return:
        """
        path = "servers/{serverId}/properties/{prop}".format(serverId=serverId, prop=prop)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Property {prop} removed from server {serverId}!"
                         .format(prop=prop, serverId=serverId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_serverNetIface(self, serverId, ifaceId):
        """
        This method will remove a Network Interface from a server.

        :param serverId: unique server Id
        :param ifaceId: Network Interface ID.
        :return:
        """
        path = "{serverId}/serverNetworkInterfaces/{ifaceId}".format(serverId=serverId, ifaceId=ifaceId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Remove Network Interface {ifaceId}!".format(ifaceId=ifaceId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_serverNetIfaceIp(self, serverId, ifaceId, ipAddress):
        """
        This method will remove a Network Interface from a server.

        :param serverId: unique server Id
        :param ifaceId: netIfaceId where IP is connected to.
        :param ipAddress: IP Address to be removed.
        :return:
        """
        path = "{serverId}/serverNetworkInterfaces/{ifaceId}/serverNetworkInterfacesIpAddress/{ipAddress}"\
            .format(serverId=serverId, ifaceId=ifaceId, ipAddress=ipAddress)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Remove IP {ipAddress} from Network Interface {ifaceId}!".format(ifaceId=ifaceId,
                                                                                          ipAddress=ipAddress))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_software(self, softwareId):
        """
        This method will remove the software.

        :param softwareId: ID of the software to be removed.
        :return:
        """
        url = self.url_base + "software/{softwareId}".format(softwareId=softwareId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            msg = "Software {softId} removed".format(softId=softwareId)
            logging.info(msg)
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_softInst(self, serverId, softId, softInstId):
        """
        This method will remove the softInstance ID. This is the first step to remove the link from server to
        application.

        :param serverId:
        :param softId:
        :param softInstId:
        :return:
        """
        url = self.url_base + "softwareInstances/{serverId}/{softwareId}/{softwareInstanceId}"\
            .format(serverId=serverId, softwareId=softId, softwareInstanceId=softInstId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            msg = "Link between server {sid} and software {softId} removed".format(sid=serverId, softId=softId)
            logging.info(msg)
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_softInst_property(self, inst_rec, propname):
        """
        This method will remove a property from a software Instance.

        :param inst_rec: Software Instance record, containing instId, softId, serverID
        :param propname: propertyName
        :return:
        """
        instId = inst_rec["instId"]
        softId = inst_rec["softId"]
        serverId = inst_rec["serverId"]
        path = "softwareInstances/{serverId}/{softId}/{instId}/properties/{prop}"\
            .format(softId=softId, instId=instId, prop=propname, serverId=serverId)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Property {prop} removed to softInst {instId}!"
                         .format(prop=propname, instId=instId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_solComp_contact(self, solId, solInstId, personId, role):
        """
        This method will remove a contact in a role from a solution component.

        :param solId: ID of the solution.
        :param solInstId: ID of the solution component
        :param personId: email of the person
        :param role: role for the person
        :return:
        """
        path = "solutions/{solId}/solutionInstances/{solInstId}/contactPersons/{personId}/{role}"\
            .format(solId=solId, solInstId=solInstId, personId=personId, role=role)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Person {email} removed from solComp {solInstId}!"
                         .format(email=personId, solInstId=solInstId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_solComp_property(self, solcomp_rec, propname):
        """
        This method will remove a property from a solution component.

        :param solcomp_rec:
        :param propname: property to be removed
        :return:
        """
        solId = solcomp_rec["solId"]
        solInstId = solcomp_rec["solInstId"]
        path = "solutions/{solId}/solutionInstances/{solInstId}/properties/{prop}"\
            .format(solId=solId, solInstId=solInstId, prop=propname)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Property {prop} removed from solComp {solInstId}!"
                         .format(prop=propname, solInstId=solInstId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_solInstComp(self, solInstId, softInstId, solId, serverId, softId):
        """
        This method will remove a solutionInstanceComponent as the final link between solution and server.

        :param solInstId: ID of the solution Component
        :param softInstId: ID of the software Instance
        :param solId: ID of the solution
        :param serverId: ID of the server
        :param softId: ID of the software
        :return:
        """
        # solutionInstanceId = solInst_rec["solInstId"]
        # softwareInstanceId = softInst_rec["instId"]
        server = dict(serverId=serverId)
        software = dict(softwareId=softId)
        solution = dict(solutionId=solId)
        softwareInstance = dict(
            softwareInstanceId=softInstId,
            software=software,
            server=server
        )
        solutionInstance = dict(
            solutionInstanceId=solInstId,
            solution=solution
        )
        sIC = solInstId + " " + softInstId
        payload = dict(
            solSoftId=sIC,
            solutionInstance=solutionInstance,
            softwareInstance=softwareInstance
        )
        data = json.dumps(payload)
        logging.debug("Payload: {p}".format(p=data))
        url = self.url_base + 'solutionInstanceComponents'
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("solution Instance Component {sIC} is removed!".format(sIC=sIC))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_solToSol(self, solToSolId, fromSolId, toSolId):
        """
        This method will remove a solution to solution relation.

        :param solToSolId: ID of the solution to Solution Component
        :param fromSolId: ID of the Source Solution Component
        :param toSolId: ID of the Target Solution Component.
        :return:
        """
        url = self.url_base + 'solutionToSolution/{fromSolId}/{toSolId}/{solToSolId}'.format(fromSolId=fromSolId,
                                                                                             toSolId=toSolId,
                                                                                             solToSolId=solToSolId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("solution to Solution {sIC} is removed!".format(sIC=solToSolId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_solutionInstance(self, solId, solInstId):
        """
        This method will remove a solutionInstance. No additional checking is done, when the function is called then
        remove is executed.

        :param solId:
        :param solInstId:
        :return:
        """
        url = self.url_base + "solutions/{solId}/solutionInstances/{solInstId}".format(solId=solId, solInstId=solInstId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            msg = "solution Instance *{solInstId}* has been deleted from solution *{solId}*".format(solId=solId,
                                                                                                    solInstId=solInstId)
            logging.info(msg)
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_solution_contact(self, solId, personId, role):
        """
        This method will remove a Person from a solution in a role.

        :param solId: ID of the solution
        :param personId: email of to the Person.
        :param role: Role of the person
        :return:
        """
        path = "solutions/{solId}/contactPersons/{personId}/{role}".format(solId=solId, personId=personId, role=role)
        url = self.url_base + path
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("Contact {personId} role {r} removed from solution {solId}!".format(solId=solId,
                                                                                             personId=personId,
                                                                                             r=role))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def remove_solution_property(self, solId, propertyName):
        """
        This method will remove a property attached to a solution

        :param solId:
        :param propertyName:
        :return:
        """
        url = self.url_base + "solutions/{solId}/properties/{prop}".format(solId=solId, prop=propertyName)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.delete(url, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            msg = "Property {prop} has been deleted from solution {solId}".format(solId=solId, prop=propertyName)
            logging.info(msg)
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return

    def update_solution_component(self, solcomp_rec):
        """
        This method will update a solution Component record.

        :param solcomp_rec: Solution Component Record.
        :return:
        """
        solId = solcomp_rec["solId"]
        solInstId = solcomp_rec["solInstId"]
        solution = dict(solutionId=solId)
        payload = dict(
            solutionInstanceId=solInstId,
            solutionInstanceName=solcomp_rec["solInstName"],
            solutionInstanceType=solcomp_rec["solInstType"],
            solution=solution
        )
        solcomp_rec.update(payload)
        for key in ["solInstId", "solInstName", "solInstType"]:
            del solcomp_rec[key]
        data = json.dumps(solcomp_rec)
        logging.debug("Payload: {p}".format(p=data))
        url = self.url_base + 'solutions/{solId}/solutionInstances/{solInstId}'\
            .format(solId=solId, solInstId=solInstId)
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        r = requests.put(url, data=data, headers=headers, auth=(self.user, self.passwd))
        if r.status_code == 200:
            logging.info("solution Instance {solInstId} is modified for solution {solId}!".format(solId=solId,
                                                                                                  solInstId=solInstId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return
