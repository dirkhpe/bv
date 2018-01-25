"""
This script will analyze the file running_software from universal discovery.
"""

import csv
# import logging
from lib import my_env
from lib import localstore
from lib.localstore import *
from sqlalchemy.orm.exc import NoResultFound


def handle_server(name):
    servername = name.strip()
    try:
        server = ds.query(Server).filter_by(name=servername).one()
    except NoResultFound:
        server = Server(
            name=servername,
            os="unk"
        )
        ds.add(server)
        ds.commit()
        ds.refresh(server)
    return server.id


field_list = ["from_server", "relationship", "counter", "to_servers"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
db = cfg['Main']['db']
ds, engine = localstore.init_session(db=db)
comm_file = cfg['Main']['server2server']
with open(comm_file, newline='') as comm_inv:
    # delimiter defaults to , - quotechar defaults to "
    comm_reader = csv.reader(comm_inv)
    # Skip first 2 lines
    next(comm_reader)
    next(comm_reader)
    loop = my_env.LoopInfo("ServerToServer", 10)
    for row in comm_reader:
        loop.info_loop()
        line = {}
        if len(row) == 4:
            for cnt in range(len(row)):
                line[field_list[cnt]] = row[cnt]
            from_server_id = handle_server(line["from_server"])
            [commtype, port] = line["relationship"].split(":")
            for to_server in line["to_servers"].split(","):
                to_server_id = handle_server(to_server)
                comm = ServerToServer(
                    from_server_id=from_server_id,
                    to_server_id=to_server_id,
                    commType=commtype,
                    port=port
                )
                ds.add(comm)
        else:
            logging.error("Unexpected Line: {l}".format(l=line))
    loop.end_loop()
