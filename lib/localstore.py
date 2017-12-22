"""
This module consolidates database access for BellaVista project.
"""

# import logging
import os
import sqlite3
from sqlalchemy import Column, Integer, Text, create_engine, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Software(Base):
    """
    Table containing the Software objects. A Software object is a package that can be ordered from a vendor for
    installation on one or many Servers.
    The software name + version makes the software unique.
    """
    __tablename__ = "software"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    label = Column(Text, nullable=False)
    version = Column(Text, nullable=True)
    vendor = Column(Text, nullable=True)
    category = Column(Text, nullable=False)
    sw_version = UniqueConstraint("name", "version")
    instances = relationship("Instance")


class Instance(Base):
    """
    Table containing the software instances. This is an installation of a Software product (object) on a server. Note
    that a software product can be installed multiple times on a server.
    """
    __tablename__ = "instance"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    version = Column(Text, nullable=True)
    ip = Column(Text, nullable=True)
    installed_path = Column(Text, nullable=True)
    port = Column(Text, nullable=True)
    software_id = Column(Integer, ForeignKey("software.id"), nullable=False)
    server_id = Column(Integer, ForeignKey("server.id"), nullable=False)
    processes = relationship("Process")


class Server(Base):
    """
    Table containing the Servers.
    """
    __tablename__ = "server"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    os = Column(Text, nullable=True)
    instances = relationship("Instance")
    # comm_from = relationship("ServerToServer", back_populates="from_server")
    # comm_to = relationship("ServerToServer", back_populates="to_server")


class Solution(Base):
    """
    Table containing solution information.
    """
    __tablename__ = "solution"
    solId = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    comment = Column(Text)
    complexity = Column(Text)
    inScope = Column(Text)
    origin = Column(Text)
    customerBusinessUnit = Column(Text)
    customerBusinessDivision = Column(Text)
    supportBusinessUnit = Column(Text)
    supportBusinessDivision = Column(Text)
    longDescription = Column(Text)
    description = Column(Text)
    applicationTreatment = Column(Text)
    classification = Column(Text)


class SolutionToSolution(Base):
    """
    Table containing solution to solution information.
    """
    __tablename__ = "solutionToSolution"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fromSolId = Column(Text, ForeignKey("solution.solId"), nullable=False)
    fromSol = relationship("Solution", foreign_keys=[fromSolId])
    fromSolName = Column(Text, nullable=False)
    toSolId = Column(Text, ForeignKey("solution.solId"), nullable=False, )
    toSol = relationship("Solution", foreign_keys=[toSolId])
    toSolName = Column(Text, nullable=False)
    conType = Column(Text)
    conSubType = Column(Text)
    conDirection = Column(Text)
    middlewareDependency = Column(Text)
    comment = Column(Text)
    description = Column(Text)


class Process(Base):
    """
    Table containing the process information. An instance must have at least one process, but can have multiple
    different processes.
    """
    __tablename__ = "process"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    commandline = Column(Text, nullable=True)
    parameters = Column(Text, nullable=True)
    path = Column(Text, nullable=True)
    instance_id = Column(Integer, ForeignKey("instance.id"), nullable=False)
    listeners = relationship("Listener")


class Listener(Base):
    """
    Table containing the listener information.
    """
    __tablename__ = "listener"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    process_id = Column(Integer, ForeignKey("process.id"), nullable=False)


class ServerToServer(Base):
    """
    Table containing the server-to-server communication information as discovered in Universal Discovery.
    """
    __tablename__ = "serverToServer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_server_id = Column(Integer, ForeignKey("server.id"), nullable=False)
    from_server = relationship("Server", foreign_keys=[from_server_id])
    to_server_id = Column(Integer, ForeignKey("server.id"), nullable=False)
    to_server = relationship("Server", foreign_keys=[to_server_id])
    commType = Column(Text, nullable=False)
    port = Column(Integer)


class DbUtils:
    """
    This class consolidates a number of Database utilities, such as rebuild of the database or rebuild of a specific
    table.
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
            # db_conn.row_factory = sqlite3.Row
            logging.debug("Datastore object and cursor are created")
            return db_conn, db_conn.cursor()
        else:
            return False, False

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




class DirectConn:
    """
    This class will set up a direct connection to the database. It allows to reset the database,
    in which case the database will be dropped and recreated, including all tables.
    """
    # Todo: Drop this class and use DbUtils instead.

    def __init__(self, config):
        """
        To drop a database in sqlite3, you need to delete the file.
        """
        self.conn_string = "sqlite:///{db}".format(db=self.db)
        self.db = config['Main']['db']
        self.dbConn = ""
        self.cur = ""

    def _connect2db(self):
        """
        Internal method to create a database connection and a cursor. This method is called during object
        initialization.
        Note that sqlite connection object does not test the Database connection. If database does not exist, this
        method will not fail. This is expected behaviour, since it will be called to create databases as well.

        :return: Database handle and cursor for the database.
        """
        # logging.debug("Creating Datastore object and cursor")
        db_conn = sqlite3.connect(self.db)
        # db_conn.row_factory = sqlite3.Row
        # logging.debug("Datastore object and cursor are created")
        return db_conn, db_conn.cursor()

    def rebuild(self):
        # A drop for sqlite is a remove of the file
        try:
            os.remove(self.db)
        except FileNotFoundError:
            pass
        # Reconnect to the Database
        self.engine = set_engine(conn_string=self.conn_string)
        Base.metadata.create_all(self.engine)


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
