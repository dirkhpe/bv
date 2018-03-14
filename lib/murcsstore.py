"""
This module consolidates data extract from Murcs.
The idea is to use SQL calls to query the database and use the Restfull API to modify the database.
"""
import logging
import pymysql


class Murcs:
    """
    This class will set up a direct connection to MySQL.
    For Drupal lkb this seems a better idea than emulating the database in a SQLAlchemy way.
    """

    def __init__(self, cfg):
        """
        The init procedure will set-up Connection to the Database Server, but not to a specific database.

        :param cfg: Link to the configuration object.
        """

        self.mysql_conn = dict(
            host=cfg['MurcsDB']['host'],
            port=int(cfg['MurcsDB']['port']),
            user=cfg['MurcsDB']['user'],
            passwd=cfg['MurcsDB']['passwd'],
            db=cfg['MurcsDB']['db']
        )
        self.conn, self.cur = self.connect2db()
        clientId = cfg['Murcs']['clientId']
        self.client_id = self.get_client(clientId)
        if not self.client_id:
            logging.error("No ID found for client {c}".format(c=clientId))

    def connect2db(self):
        self.conn = pymysql.connect(**self.mysql_conn)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        return self.conn, self.cur

    def close(self):
        self.conn.close()

    def recycle(self):
        self.close()
        self.connect2db()

    def get_table(self, tablename):
        """
        This method will return the table as a list of named rows. This means that each row in the list will return
        the table column value as an attribute. E.g. row.name will return the value for column name in each row.
        :param tablename:
        :return:
        """
        query = "SELECT * FROM {t}".format(t=tablename)
        self.cur.execute(query)
        res = self.cur.fetchall()
        return res

    def get_client(self, clientid):
        """
        This method will get the id of the client for this clientId, or False if the client is not found.

        :param clientid: clientId (name) for this client.

        :return: id (number) of the client, or False if the client does not exist.
        """
        query = "SELECT id FROM client WHERE clientId=%(id)s"
        self.cur.execute(query, {"id": clientid})
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]['id']
        else:
            return False

    def get_server(self, hostName):
        """
        This method will return the id of the server for this hostName, or False if no server is found for the hostName
        and the clientId.

        :param hostName:

        :return: Dict with id and serverId of the server, or False if the server does not exist.
        """
        query = "SELECT * FROM server WHERE hostName=%(hostName)s AND clientId=%(client_id)s"
        self.cur.execute(query, {"hostName": hostName, "client_id": self.client_id})
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return False

    def get_soft(self, softId):
        """
        This method will return the soft record for this softId, or False if no software is found for the softId
        and the clientId.

        :param softId:

        :return: Dict with the first software record, or False if the software does not exist.
        """
        query = "SELECT * FROM soft WHERE softId=%(softId)s AND clientId=%(client_id)s"
        self.cur.execute(query, {"softId": softId, "client_id": self.client_id})
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return False

    def get_softInst(self, soft_id, server_id, softInstId=False):
        """
        This method will return the software instance linking the solution to the server. Soft_id and server_id are
        required to guarantee we are extracting data for the required clientID (and not for previous/next version of
        the client load in Murcs).

        :param soft_id: id (number) of the soft record

        :param server_id: id (number) of the server record.

        :param softInstId: Optional. By default "softId serverId". In case this is softInstance for Application, then
        environment will be added if it is other than 'Production'. Current environments are Production, Development
        and Quality.

        :return:
        """
        cols = dict(
            server_id=server_id,
            soft_id=soft_id
        )
        if softInstId:
            cols["softInstId"] = softInstId
            query_app = " AND instId=%(softInstId)s"
        else:
            query_app = ""
        query = "SELECT * FROM softinst WHERE serverId=%(server_id)s AND softId=%(soft_id)s" + query_app
        self.cur.execute(query, cols)
        res = self.cur.fetchall()
        if len(res) > 0:
            logging.debug("Connection Server {h} to Software {sw} established.".format(h=server_id, sw=soft_id))
            return res[0]
        else:
            logging.debug("Connection Server {h} to Software {sw} not found.".format(h=server_id, sw=soft_id))
            return False

    def get_softInst_fromId(self, instId):
        """
        This method will return the software instance record for a specific instance Id. This is required to link a
        database (schema) to more than one application, or to add a property to a software Instance.

        :param instId: ID of the instance.

        :return: instance record or False if not found. Attributes include instId, softId, serverID and id.
        """
        query = """
            SELECT i.id as id, i.instId as instId, h.serverId as serverId, s.softId as softId
            FROM softinst i
            INNER JOIN soft s on s.id = i.softId
            INNER JOIN server h on h.id=i.serverId
            WHERE instId=%(instId)s
              AND h.id=i.serverId
              AND s.clientId = %(client_id)s
        """
        cols = dict(
            instId=instId,
            client_id=self.client_id
        )
        self.cur.execute(query, cols)
        res = self.cur.fetchall()
        if len(res) > 0:
            logging.debug("Instance {instId} found.".format(instId=instId))
            return res[0]
        else:
            logging.debug("Instance {instId} not found.".format(instId=instId))
            return False

    def get_softInst_os(self, hostName):
        """
        This method will return the software instance record for an Operating System attached to a servername.

        :param hostName: hostName of the server.

        :return: instance record or False if not found.
        """
        query = """
            SELECT i.id as id, i.instId as instId, h.serverId as serverId, s.softId as softId
            FROM softinst i
            INNER JOIN soft s on s.id = i.softId
            INNER JOIN server h on h.id=i.serverId
            WHERE h.hostName=%(hostName)s
              AND h.id=i.serverId
              AND s.clientId = %(client_id)s
              AND i.instType = %(instType)s
        """
        cols = dict(
            hostName=hostName,
            client_id=self.client_id,
            instType='OperatingSystem'
        )
        self.cur.execute(query, cols)
        res = self.cur.fetchall()
        if len(res) > 0:
            logging.debug("OS Instance for host {hostName} found.".format(hostName=hostName))
            return res[0]
        else:
            logging.error("OS Instance for {hostName} not found.".format(hostName=hostName))
            return False

    def get_sol(self, solId):
        """
        This method will return the id of the solution for this solId, or False if no solution is found for the solId
        and the clientId.

        :param solId:

        :return: Dict with the first solution record, or False if the solution does not exist.
        """
        query = "SELECT * FROM sol WHERE solId=%(solId)s AND clientId=%(client_id)s"
        self.cur.execute(query, {"solId": solId, "client_id": self.client_id})
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return False

    def get_solInst(self, solId):
        """
        This method will return the solInstId linked with the solution solId.
        Note that it is possible to have more than one solInstId related to a solId. Use function get_solComp to
        approach a solComp directly.

        :param solId: Solution for which solInstId is required. Client ID is used while requesting solution record.

        :return: solInstId, or False if not found.
        """
        sol_id = self.get_sol(solId)["id"]
        query = "SELECT * FROM solinst WHERE solId=%(solId)s"
        self.cur.execute(query, {"solId": sol_id})
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return False

    def get_solComp(self, solInstId):
        """
        This method will return the solComp record linked with the solInstId.

        :param solInstId: solInstId for which record is required.

        :return: solInstId, or False if not found.
        """
        query = """
            SELECT s.solId as solId, s.solName as solName, i.environment as environment, i.id as id,
                   i.solInstId as solInstId, i.solInstName as solInstName, i.solInstType as solInstType
            FROM solinst i
            INNER JOIN sol s on s.id=i.solId
            WHERE solInstId=%(solInstId)s
              AND s.clientId=%(client_id)s
        """
        params = dict(
            solInstId=solInstId,
            client_id=self.client_id
        )
        self.cur.execute(query, params)
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return False

    def get_solInstComp(self, solInst_id, softInst_id):
        """
        This method will return the solInstComp record linked with the solution and the server.

        :param solInst_id: id (number) of the Solution Component.

        :param softInst_id: id (number) of the software instance.

        :return: solInstComp record, or False if not found.
        """
        query = "SELECT * FROM solinstcomponent WHERE softInstId=%(softInst_id)s AND solInstId=%(solInst_id)s"
        self.cur.execute(query, {"softInst_id": softInst_id, "solInst_id": solInst_id})
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return False
