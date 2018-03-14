"""
This script will add a software Instance Property.
A usage is for an application instance to add a functional description of the software Instance in this application.
A solution component is common per environment, one instantiation of the solution. The software instance is unique for
the server. So if the server has a specific function in the application, this specific function will be described as
the 'Function' property in the Software Instance.
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
        description="Add a property to a software Instance"
    )
    parser.add_argument('-i', '--instId', type=str, required=True,
                        help='Please provide software instId for which a property needs to be added.')
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='Select property')
    parser.add_argument('-v', '--value', type=str, required=True,
                        help='Please provide property value')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    inst_rec = mdb.get_softInst_fromId(args.instId)
    if inst_rec:
        # Check if this is a known property
        name_key = "{prop}_name".format(prop=args.name)
        desc_key = "{prop}_description".format(prop=args.name)
        try:
            propertyName = cfg["serverProps"][name_key]
            description = cfg["serverProps"][desc_key]
        except KeyError:
            sys.exit("property identifier {prop} not found...".format(prop=args.name) )
        unique_propname = "{prop}_{id}".format(prop=propertyName, id=inst_rec["id"])
        payload = dict(
            propertyName=unique_propname,
            propertyValue=args.value,
            description = "{desc} - {now:%Y-%m-%d}".format(desc=description, now=datetime.datetime.now())
        )
        r.add_softInst_property(inst_rec, payload)
    else:
        logging.error("Software Instance with id {id} not found!".format(id=args.instId))
    mdb.close()
