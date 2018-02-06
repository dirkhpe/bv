"""
This script will add a solution Component Property.
"""
import argparse
import logging
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Add a property to a solution Component to a solution"
    )
    parser.add_argument('-a', '--solId', type=str, required=True,
                        help='Please provide solId for which a property needs to be added.')
    parser.add_argument('-e', '--env', type=str, required=True,
                        choices=['Production', 'Development', 'Quality', 'Compression'],
                        help='Select environment (Production, Development, Quality, Compression)')
    parser.add_argument('-n', '--name', type=str, required=True,
                        choices=['sid'],
                        help='Select property (sid)')
    parser.add_argument('-v', '--value', type=str, required=True,
                        help='Please provide property value')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    solInstId = my_env.get_solInstId(solId=args.solId, env=args.env)
    solInst_rec = mdb.get_solComp(solInstId)
    solId = solInst_rec["solId"]
    payload = dict(
        propertyName="SAP_SID",
        propertyValue=args.value,
        description="SAP System Identifier"
    )
    r.add_solComp_property(solInst_rec, payload)
    mdb.close()
