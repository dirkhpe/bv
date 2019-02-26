"""
This script will analyze the file running_software from universal discovery.

"""

import csv
import logging
from lib import my_env
from lib import localstore
from lib.localstore import *
from sqlalchemy.orm.exc import NoResultFound


def handle_software(**params):
    try:
        soft = ds.query(Software).filter_by(name=params["name"], version=params["version"]).one()
    except NoResultFound:
        if params["label"] == "Active Directory Application Mode":
            params["category"] = params["label"]
        soft = Software(
            name=params["name"],
            label=params["label"],
            version=params["version"],
            vendor=params["vendor"],
            category=params["category"]
        )
        ds.add(soft)
        ds.commit()
        ds.refresh(soft)
    return soft.id


def handle_server(**params):
    try:
        server = ds.query(Server).filter_by(name=params["name"]).one()
    except NoResultFound:
        server = Server(
            name=params["name"],
            os=params["os"]
        )
        ds.add(server)
        ds.commit()
        ds.refresh(server)
    return server.id


def handle_instance(**params):
    # This needs to be a new / separate instance.
    # It will be different from any other instance, but we are not sure which columns are different.
    instance = SoftwareInstance(
        name=params["name"],
        version=params["version"],
        ip=params["ip"],
        installed_path=params["installed_path"],
        port=params["port"],
        server_id=params["server_id"],
        software_id=params["software_id"]
    )
    ds.add(instance)
    ds.commit()
    ds.refresh(instance)
    return instance.id


field_list = ["software_label", "instance_name", "software_category", "instance_ip", "instance_installed_path",
              "instance_port", "instance_version", "software_name", "software_vendor", "software_version",
              "server_name", "server_os", "process_name", "process_commandline", "process_parameters",
              "process_path", "listener_name"]

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
db = cfg['Main']['db']
ds, engine = localstore.init_session(db=db)
sw_file = cfg['Main']['running_sw']

with open(sw_file, newline='') as sw_inv:
    # delimiter defaults to , - quotechar defaults to "
    sw_reader = csv.reader(sw_inv)
    # Skip first 2 lines
    next(sw_reader)
    next(sw_reader)
    server_id = -1
    software_id = -1
    instance_id = -1
    process_id = -1
    loop = my_env.LoopInfo("Running_Software", 10)
    for row in sw_reader:
        loop.info_loop()
        line = {}
        if len(row) == 17:
            for cnt in range(len(row)):
                line[field_list[cnt]] = row[cnt]
            if len(line["listener_name"]) > 0:
                # This needs to be a listener associated with a process
                listener = Listener(
                    name=line["listener_name"],
                    process_id=process_id
                )
                ds.add(listener)
                ds.commit()
            elif len(line["process_name"]) > 0:
                # This needs to be a process associated with an instance
                process = Process(
                    name=line["process_name"],
                    commandline=line["process_commandline"],
                    parameters=line["process_parameters"],
                    path=line["process_path"],
                    instance_id=instance_id
                )
                ds.add(process)
                ds.commit()
                ds.refresh(process)
                process_id = process.id
            elif len(line["server_name"]) > 0:
                # New line with Instance level
                software_id = handle_software(
                    name=line["software_name"],
                    label=line["software_label"],
                    version=line["software_version"],
                    vendor=line["software_vendor"],
                    category=line["software_category"]
                )
                server_id = handle_server(
                    name=line["server_name"],
                    os=line["server_os"]
                )
                instance_id = handle_instance(
                    name=line["instance_name"],
                    version=line["instance_version"],
                    ip=line["instance_ip"],
                    installed_path=line["instance_installed_path"],
                    port=line["instance_port"],
                    software_id=software_id,
                    server_id=server_id
                )
            else:
                logging.error("Unexpected Line: {l}".format(l=line))
    loop.end_loop()
