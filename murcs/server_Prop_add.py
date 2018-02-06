"""
This script will add a server Property.
"""
import argparse
import logging
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
                        choices=['oos'],
                        help='Select property (oos for Server Out of Scope reason)')
    parser.add_argument('-v', '--value', type=str, required=True,
                        help='Please provide property value')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    hostName = args.hostName
    server_rec = mdb.get_server(hostName)
    payload = dict(
        propertyName="OutOfScope",
        propertyValue=args.value,
        description="Reason why this server is Out Of Scope"
    )

    r.add_server_property(server_rec, payload)
    mdb.close()
