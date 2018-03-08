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
        self.user = cfg['Murcs']['user']
        self.passwd = cfg['Murcs']['passwd']
        host = cfg['Murcs']['host']
        port = cfg['Murcs']['port']
        clientId = cfg['Murcs']['clientId']
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

    def add_server_property(self, server_rec, payload):
        """
        This method will add a property to a server.

        :param server_rec:

        :param payload: Dictionary with propertyName, propertyValue and description

        :return:
        """
        serverId = server_rec["serverId"]
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
        This method will load a server in Murcs.

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

    def get_sol(self, solId):
        """
        This method launches the Rest call to get the solution information

        :param solId:

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
            logging.info("Load server {email}!".format(email=email))
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

    def add_softInst(self, softId, serverId, **params):
        """
        This method will link a Software from a solution to a server.
        By default the softInstId is "softId serverId". In case this is softInstance for Application, then
        environment will be added if it is other than 'Production'. Current environments are Production, Development
        and Quality. Environment is also in instSubType then.
        In case this is a database with a known schema, instSubType will have the schema name.

        :param softId: ID Name for the Software

        :param serverId: ID Name for the Server

        :param params: dictionary with additional attributes. softInstId is mandatory for Type 'Application' Type and
        environment not Production. instSubType: (Optional) Schema of the instance, or environment for Application-type
        software instances. instType: Defaults to 'Application'

        :return:
        """
        try:
            softwareInstanceId = params["softInstId"]
        except KeyError:
            softwareInstanceId = "{softId} {serverId}".format(softId=softId, serverId=serverId)
        try:
            softwareInstanceType = params["instType"]
        except KeyError:
            softwareInstanceType = "Application"
        server = dict(serverId=serverId)
        software = dict(softwareId=softId)
        payload = dict(
            softwareInstanceId=softwareInstanceId,
            softwareInstanceType=softwareInstanceType,
            server=server,
            software=software
        )
        try:
            payload["instanceSubType"] = params["instSubType"]
        except KeyError:
            pass
        try:
            payload["description"] = params["description"]
        except KeyError:
            pass
        data = json.dumps(payload)
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

    def add_solInstComp(self, solInstId, softInstId, solId, serverId, softId):
        """
        This method will add a solutionInstanceComponent as the final link between solution and server.

        :param solInstId:

        :param softInstId:

        :param solId:

        :param serverId:

        :param softId:

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
        Component need to be used.

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
            logging.info("Contact {personId} removed from solution {solId}!".format(solId=solId, personId=personId))
        else:
            logging.fatal("Investigate: {s}".format(s=r.status_code))
            logging.fatal(r.content)
            r.raise_for_status()
        return
