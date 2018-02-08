"""
This script will add a server Property.
"""
import argparse
import datetime
import logging
import sys
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Add a property to a server"
    )
    parser.add_argument('-s', '--hostName', type=str, required=True,
                        help='Please provide hostName to identify the server.')
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='Select property for Server')
    parser.add_argument('-v', '--value', type=str, required=True,
                        help='Please provide property value')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Check if this is a known property for the server
    name_key = "{prop}_name".format(prop=args.name)
    desc_key = "{prop}_description".format(prop=args.name)
    try:
        propertyName = cfg["serverProps"][name_key]
        description = cfg["serverProps"][desc_key]
    except KeyError:
        sys.exit("property identifier {prop} not found...".format(prop=args.name) )
    hostName = args.hostName
    server_rec = mdb.get_server(hostName)
    payload = dict(
        propertyName=propertyName,
        propertyValue=args.value,
        description="{desc} - {now:%Y-%m-%d}".format(desc=description, now=datetime.datetime.now())
    )

    r.add_server_property(server_rec, payload)
    mdb.close()
