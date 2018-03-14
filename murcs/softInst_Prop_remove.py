"""
This script will remove a software Instance Property with a Rest call.
"""
import argparse
import logging
import sys
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Get a property to a software Instance"
    )
    parser.add_argument('-i', '--instId', type=str, required=True,
                        help='Please provide software instId for which a property needs to be removed.')
    parser.add_argument('-n', '--name', type=str, required=True,
                        help='Select property')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    inst_rec = mdb.get_softInst_fromId(args.instId)
    if inst_rec:
        # Check if this is a known property
        name_key = "{prop}_name".format(prop=args.name)
        try:
            propertyName = cfg["serverProps"][name_key]
        except KeyError:
            sys.exit("property identifier {prop} not found...".format(prop=args.name) )
        unique_propname = "{prop}_{id}".format(prop=propertyName, id=inst_rec["id"])
        r.remove_softInst_property(inst_rec, unique_propname)
    else:
        logging.error("Software Instance with id {id} not found!".format(id=args.instId))
    mdb.close()
