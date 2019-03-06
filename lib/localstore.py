"""
This module consolidates database access for BellaVista project.
"""

import logging
import os
import pymysql
import sqlite3
from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class ContactServer(Base):
    """
    Table containing contact persons and roles per server.
    """
    __tablename__ = "contactserver"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    email = Column(Text)
    role = Column(Text)
    serverId = Column(Text)


class ContactSolution(Base):
    """
    Table containing contact persons and roles per solution.
    """
    __tablename__ = "contactsolution"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    email = Column(Text)
    role = Column(Text)
    solutionId = Column(Text)


class NetworkIpAddress(Base):
    """
    Table containing the Network IP Address Information.
    """
    __tablename__ = "ipaddress"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    dns1 = Column(Text)
    dns2 = Column(Text)
    dnsSearchList = Column(Text)
    dnsSuffix = Column(Text)
    fqdns = Column(Text)
    gateway = Column(Text)
    ipAddress = Column(Text)
    ipAddressType = Column(Text)
    name = Column(Text)
    netmask = Column(Text)
    serverNetworkInterface = Column(Text)
    serverNetworkInterfaceId = Column(Text)
    vCenterNIC = Column(Text)
    vLanId = Column(Text)


class NetworkInterface(Base):
    """
    Table containing the Network Interface Information.
    """
    __tablename__ = "netiface"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    duplex = Column(Text)
    interfaceName = Column(Text)
    macAddress = Column(Text)
    negotiation = Column(Text)
    networkInterfaceId = Column(Text)
    serverId = Column(Text)
    speedMB = Column(Integer)


class Person(Base):
    """
    Table containing the Person Information.
    """
    __tablename__ = "person"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    address = Column(Text)
    company = Column(Text)
    department = Column(Text)
    email = Column(Text)
    firstName = Column(Text)
    lastName = Column(Text)
    mobilePhoneNo = Column(Text)
    phoneNo = Column(Text)
    searchEmail = Column(Text)
    title = Column(Text)


class Server(Base):
    """
    Table containing the Server Information.
    """
    __tablename__ = "server"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    availability = Column(Text)
    backupInformation = Column(Text)
    brand = Column(Text)
    category = Column(Text)
    classification = Column(Text)
    clockSpeedGhz = Column(Integer)
    clusterArchitecture = Column(Text)
    clusterName = Column(Text)
    clusterTechnologie = Column(Text)
    cmdbSystemId = Column(Integer)
    contact = Column(Text)
    contractServiceLevel = Column(Text)
    coreCount = Column(Integer)
    coverage = Column(Text)
    cpuCount = Column(Integer)
    cpuType = Column(Text)
    currentApproach = Column(Text)
    disasterRecoveryServer = Column(Text)
    domain = Column(Text)
    fqdn = Column(Text)
    futureApproach = Column(Text)
    hostName = Column(Text)
    hwModel = Column(Text)
    hyperThreading = Column(Text)
    inScope = Column(Text)
    insideDMZ = Column(Text)
    installationDate = Column(Text)
    lifeCycleState = Column(Text)
    macAddress = Column(Text)
    managementRegion = Column(Text)
    memorySizeInByte = Column(Integer)
    murcsScope = Column(Text)
    operatingSystem = Column(Text)
    operatingSystemVersion = Column(Text)
    parentServer = Column(Text)
    primaryIPAddress = Column(Text)
    ragState = Column(Text)
    securityClass = Column(Text)
    serialNo = Column(Text)
    serverId = Column(Text)
    serverType = Column(Text)
    serverUsage = Column(Text)
    serverUsageDetailed = Column(Text)
    service = Column(Text)
    servicePack = Column(Text)
    siteId = Column(Text)
    sla = Column(Text)
    status = Column(Text)
    subCategory = Column(Text)
    subtype = Column(Text)
    supportGroup = Column(Text)
    systemLocation = Column(Text)
    technicalOwner = Column(Text)
    technicalOwnerBackup = Column(Text)
    timeZone = Column(Text)
    usageContact = Column(Text)
    vCenter = Column(Text)
    virtualizationRole = Column(Text)
    virtualizationTechnologie = Column(Text)
    virtualizationUUID = Column(Text)


class ServerProperty(Base):
    """
    Table containing the Server Property Information.
    """
    __tablename__ = "serverproperty"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    description = Column(Text)
    propertyName = Column(Text)
    propertyValue = Column(Text)
    serverId = Column(Text)


class Site(Base):
    """
    Table containing the Site information
    """
    __tablename__ = "site"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    country = Column(Text)
    dataCenterName = Column(Text)
    description = Column(Text)
    eslId = Column(Integer)
    siteId = Column(Text)
    provider = Column(Text)
    region = Column(Text)
    town = Column(Text)


class Software(Base):
    """
    Table containing the Software objects. A Software object is a package that can be ordered from a vendor for
    installation on one or many Servers.
    The software name + version makes the software unique.
    """
    __tablename__ = "software"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    comment = Column(Text)
    description = Column(Text)
    inScope = Column(Text)
    installationPackageAvailable = Column(Text)
    longDescription = Column(Text)
    ragState = Column(Text)
    softwareId = Column(Text)
    softwareName = Column(Text)
    softwareSubType = Column(Text)
    softwareType = Column(Text)
    softwareVendor = Column(Text)
    softwareVersion = Column(Text)
    state = Column(Text)
    status = Column(Text)
    supportedVersion = Column(Text)
    thirdPartySupportNeeded = Column(Text)
    instances = relationship("Instance")


class SoftwareInstance(Base):
    """
    Table containing the software instances. This is an installation of a Software product (object) on a server. Note
    that a software product can be installed multiple times on a server.
    """
    __tablename__ = "softinst"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    backup = Column(Text)
    comment = Column(Text)
    description = Column(Text)
    instanceSubType = Column(Text)
    language = Column(Text)
    patchLevel = Column(Text)
    serverId = Column(Text)
    softwareId = Column(Text)
    softwareInstanceId = Column(Text)
    softwareInstanceType = Column(Text)
    validFrom = Column(Text)
    validTo = Column(Text)


class SolutionInstanceProperty(Base):
    """
    Table containing the Solution Instance Property Information.
    """
    __tablename__ = "solinstproperty"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    description = Column(Text)
    propertyName = Column(Text)
    propertyValue = Column(Text)
    solutionId = Column(Text)
    solutionInstanceId = Column(Text)


class Solution(Base):
    """
    Table containing solution information.
    """
    __tablename__ = "solution"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    applicationDetailTreatment = Column(Text)
    applicationTreatment = Column(Text)
    architecture = Column(Text)
    assessmentComplete = Column(Text)
    avgUserCount = Column(Text)
    classification = Column(Text)
    comment = Column(Text)
    complexity = Column(Text)
    customerBusinessDivision = Column(Text)
    customerBusinessUnit = Column(Text)
    description = Column(Text)
    externalSupportNeeded = Column(Text)
    inScope = Column(Text)
    longDescription = Column(Text)
    origin = Column(Text)
    ragScore = Column(Text)
    ragState = Column(Text)
    sla = Column(Text)
    solutionId = Column(Text)
    solutionName = Column(Text)
    state = Column(Text)
    status = Column(Text)
    supportBusinessDivision = Column(Text)
    supportBusinessUnit = Column(Text)
    watchSolution = Column(Text)


class SolutionInstance(Base):
    """
    Table containing solution Instance information.
    """
    __tablename__ = "solinst"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    availability = Column(Text)
    avgUserCount = Column(Text)
    businessCriticality = Column(Text)
    comment = Column(Text)
    coverage = Column(Text)
    description = Column(Text)
    environment = Column(Text)
    impact = Column(Text)
    maintenanceDowntimeWindow = Column(Text)
    peakUserCount = Column(Text)
    priority = Column(Text)
    ragScore = Column(Text)
    ragState = Column(Text)
    returnToOperation = Column(Text)
    scheduledReboot = Column(Text)
    sla = Column(Text)
    solutionId = Column(Text)
    solutionInstanceId = Column(Text)
    solutionInstanceName = Column(Text)
    solutionInstanceType = Column(Text)
    state = Column(Text)


class SolutionInstanceComponent(Base):
    """
    Table containing solution Instance Component information.
    """
    __tablename__ = "solinstcomp"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    availability = Column(Text)
    priority = Column(Text)
    serverId = Column(Text)
    softwareId = Column(Text)
    softwareInstanceId = Column(Text)
    solutionId = Column(Text)
    solutionInstanceId = Column(Text)
    status = Column(Text)
    validFrom = Column(Text)
    validTo = Column(Text)


class SolutionProperty(Base):
    """
    Table containing the Solution Property Information.
    """
    __tablename__ = "solutionproperty"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    description = Column(Text)
    propertyName = Column(Text)
    propertyValue = Column(Text)
    solutionId = Column(Text)


class SolutionToSolution(Base):
    """
    Table containing solution To Solution information.
    """
    __tablename__ = "soltosol"
    id = Column(Integer, primary_key=True, autoincrement=True)
    changedAt = Column(Text)
    changedBy = Column(Text)
    createdAt = Column(Text)
    createdBy = Column(Text)
    clientId = Column(Text)
    version = Column(Text)
    businessCriticality = Column(Text)
    comment = Column(Text)
    connectionDirection = Column(Text)
    connectionFrequency = Column(Text)
    connectionSubType = Column(Text)
    connectionType = Column(Text)
    connectionVolumeInByte = Column(Text)
    description = Column(Text)
    fromSolutionId = Column(Text)
    middlewareDependency = Column(Text)
    solutionToSolutionId = Column(Text)
    toSolutionId = Column(Text)


class sqliteUtils:
    """
    This class consolidates a number of Database utilities for sqlite, such as rebuild of the database or rebuild of a
    specific table.
    """

    def __init__(self, config):
        """
        To drop a database in sqlite3, you need to delete the file.
        """
        self.db = config['Main']['db']
        self.dbConn, self.cur = self._connect2db()

    def _connect2db(self):
        """
        Internal method to create an sqlalchemy database connection.
        Note that sqlite connection object does not test the Database connection. If database does not exist, this
        method will not fail. This is expected behaviour, since it will be called to create databases as well.

        :return: SqlAlchemy Database handle for the database.
        """
        if os.path.isfile(self.db):
            db_conn = sqlite3.connect(self.db)
            db_conn.row_factory = sqlite3.Row
            logging.debug("Datastore object and cursor are created")
            return db_conn, db_conn.cursor()
        else:
            return False, False

    def create_table(self, tablename, row):
        """
        This method will create a table where the fields are the row list.

        :param tablename: Name of the table
        :param row: Comma separated list with field names. First field must be Node.
        :return: Length of the row.
        """
        query = "DROP TABLE IF EXISTS {tn}".format(tn=tablename)
        logging.debug("Drop Query: {q}".format(q=query))
        self.dbConn.execute(query)
        fieldlist = ["`{field}` text".format(field=field) for field in row]
        query = "CREATE TABLE {tn} ({fields})".format(tn=tablename, fields=", ".join(fieldlist))
        logging.debug("Create Query: {q}".format(q=query))
        self.dbConn.execute(query)
        logging.info("Table {tn} is built".format(tn=tablename))
        return len(row)

    def get_query(self, query):
        """
        This method will get a query and return the result of the query.

        :param query:
        :return:
        """
        self.cur.execute(query)
        res = self.cur.fetchall()
        return res

    def get_server(self, serverId):
        """
        This method will return the server record for the server with this hostName, or False if no server is found
        for the hostName and the clientId.

        :param serverId:
        :return: Dict with server record including id and serverId of the server, or False if the server does not exist.
        """
        query = "SELECT * FROM server WHERE serverId=?"
        self.cur.execute(query, (serverId,))
        res = self.cur.fetchall()
        if len(res) > 0:
            return res[0]
        else:
            return False

    def get_softInst_os(self, serverId):
        """
        This method will return the software instance record for an Operating System attached to a serverName.

        :param serverId: serverId of the server.
        :return: instance record or False if not found.
        """
        query = """
            SELECT i.softwareInstanceId as softwareInstanceId, h.serverId as serverId, s.softwareId as softwareId
            FROM softinst i
            INNER JOIN software s on s.softwareId = i.softwareId
            INNER JOIN server h on h.serverId=i.serverId
            WHERE h.serverId=?
              AND i.softwareInstanceType = 'OperatingSystem'
        """
        self.cur.execute(query, (serverId, ))
        res = self.cur.fetchall()
        if len(res) > 0:
            logging.debug("OS Instance for host {hostName} found.".format(hostName=serverId))
            return res[0]
        else:
            logging.error("OS Instance for {hostName} not found.".format(hostName=serverId))
            return False

    def get_table(self, tablename):
        """
        This method will return the table as a list of named rows. This means that each row in the list will return
        the table column values as an attribute. E.g. row.name will return the value for column name in each row.

        :param tablename:
        :return:
        """
        query = "SELECT * FROM {t}".format(t=tablename)
        self.cur.execute(query)
        res = self.cur.fetchall()
        return res

    def insert_row(self, tablename, rowdict):
        """
        This method will insert a dictionary row into a table.

        :param tablename: Table Name to insert data into
        :param rowdict: Row Dictionary
        :return:
        """
        columns = ", ".join("`" + k + "`" for k in rowdict.keys())
        values_template = ", ".join(["?"] * len(rowdict.keys()))
        query = "insert into {tn} ({cols}) values ({vt})".format(tn=tablename, cols=columns, vt=values_template)
        values = tuple(rowdict[key] for key in rowdict.keys())
        logging.debug("Insert query: {q}".format(q=query))
        self.dbConn.execute(query, values)
        self.dbConn.commit()
        return

    def insert_rows(self, tablename, rowdict):
        """
        This method will insert a list of dictionary rows into a table.

        :param tablename: Table Name to insert data into
        :param rowdict: List of Dictionary Rows
        :return:
        """
        if len(rowdict) > 0:
            columns = ", ".join("`" + k + "`" for k in rowdict[0].keys())
            values_template = ", ".join(["?"] * len(rowdict[0].keys()))
            query = "insert into {tn} ({cols}) values ({vt})".format(tn=tablename, cols=columns, vt=values_template)
            logging.debug("Insert query: {q}".format(q=query))
            # cnt = my_env.LoopInfo(tablename, 50)
            for line in rowdict:
                # cnt.info_loop()
                logging.debug(line)
                values = tuple(line[key] for key in line.keys())
                self.dbConn.execute(query, values)
            # cnt.end_loop()
            self.dbConn.commit()
        return

    def rebuild(self):
        # A drop for sqlite is a remove of the file
        if self.dbConn:
            self.dbConn.close()
            os.remove(self.db)
        # Reconnect to the Database
        self.dbConn, self.cur = self._connect2db()
        # Use SQLAlchemy connection to build the database
        conn_string = "sqlite:///{db}".format(db=self.db)
        engine = set_engine(conn_string=conn_string)
        Base.metadata.create_all(engine)


class mysqlUtils:
    """
    This class consolidates a number of Database utilities for mySql, such as rebuild of the database or rebuild of a
    specific table.
    """

    def __init__(self, config):
        """
        The init procedure will set-up Connection to the Database Server.

        :param config: Link to the configuration object.
        """
        self.msp = dict(
            host=config['MySQL']['host'],
            port=int(config['MySQL']['port']),
            user=config['MySQL']['user'],
            passwd=config['MySQL']['passwd'],
            db=config['MySQL']['db']
        )
        self.conn = pymysql.connect(**self.msp)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)

    def rebuild(self):
        """
        This function will drop and recreate the database. Then it will call SQLAlchemy to recreate the tables.

        :return:
        """
        db = self.msp["db"]
        user = self.msp["user"]
        passwd = self.msp["passwd"]
        host = self.msp["host"]
        query = "DROP DATABASE IF EXISTS {db}".format(db=db)
        logging.info(query)
        self.cur.execute(query)
        query = "CREATE DATABASE {db}".format(db=db)
        logging.info(query)
        self.cur.execute(query)
        # Now use sqlalchemy connection to build database
        conn_string = "mysql+pymysql://{u}:{p}@{h}/{db}".format(db=db, u=user, p=passwd, h=host)
        engine = set_engine(conn_string)
        Base.metadata.create_all(engine)


def init_session(db, echo=False):
    """
    This function configures the connection to the database and returns the session object.

    :param db: Name of the sqlite3 database.
    :param echo: True / False, depending if echo is required. Default: False
    :return: Tuple consisting of session object and engine object.
    """
    conn_string = "sqlite:///{db}".format(db=db)
    engine = set_engine(conn_string, echo)
    session = set_session4engine(engine)
    return session, engine


def set_engine(conn_string, echo=False):
    engine = create_engine(conn_string, echo=echo)
    return engine


def set_session4engine(engine):
    session_class = sessionmaker(bind=engine)
    session = session_class()
    return session
