"""
This module consolidates the Murcs Rest Calls
"""
import logging
import os
import requests
import json


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
        self.url_base = "http://{host}:{port}/murcs/rest/{clientId}/".format(host=host, port=port, clientId=clientId)

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

    def get_wave(self):
        """
        This method launches the Rest call to get wave information

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

    def add_software_from_sol(self, sol_rec):
        """
        This method will create a Software from a Solution.

        :param sol_rec:

        :return:
        """
        softId = "{solId} software".format(solId=sol_rec["solId"])
        softName = "{solName} (software)".format(solName=sol_rec["solName"])
        payload = dict(
            softwareId=softId,
            softwareName=softName,
            softwareType="Application",
            softwareSubType="Application Implementation",
            softwareVersion="Production",
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

    def add_software_instance(self, soft_rec, server_rec, softInstId=False, instSubType=False):
        """
        This method will link a Software from a solution to a server.

        :param soft_rec:

        :param server_rec:

        :param softInstId:

        :param instSubType: (Optional) Schema of the instance.

        :return:
        """
        softId = soft_rec["softId"]
        serverId = server_rec["serverId"]
        if softInstId:
            softwareInstanceId = softInstId
        else:
            softwareInstanceId = "{softId} {serverId}".format(softId=softId, serverId=serverId)
        softwareInstanceType = "Application"
        server = dict(serverId=serverId)
        software = dict(softwareId=softId)
        payload = dict(
            softwareInstanceId=softwareInstanceId,
            softwareInstanceType=softwareInstanceType,
            server=server,
            software=software
        )
        if instSubType:
            payload["instanceSubType"] = instSubType
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

    def add_solInstComp(self, solInst_rec, softInst_rec, solId, serverId, softId):
        """
        This method will add a solutionInstanceComponent as the final link between solution and server.

        :param solInst_rec:

        :param softInst_rec:

        :param solId:

        :param serverId:

        :param softId:

        :return:
        """
        solutionInstanceId = solInst_rec["solInstId"]
        softwareInstanceId = softInst_rec["instId"]
        server = dict(serverId=serverId)
        software = dict(softwareId=softId)
        solution = dict(solutionId=solId)
        softwareInstance = dict(
            softwareInstanceId=softwareInstanceId,
            software=software,
            server=server
        )
        solutionInstance = dict(
            solutionInstanceId=solutionInstanceId,
            solution=solution
        )
        sIC = solutionInstanceId + " " + softwareInstanceId
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

    def add_solutionInstance(self, sol_rec):
        """
        This method will add a solution Instance to a solution.

        :param sol_rec: Solution Record.

        :return:
        """
        solId = sol_rec["solId"]
        solInstId = "{solId} solInstanceFromScript".format(solId=solId)
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
