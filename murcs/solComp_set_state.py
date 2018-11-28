"""
This script will set the status of an application component. Status In Progress means that transformation for this
component has started, Transformed means that transformation is finished and state Decommissioned means that application
component is no longer required in CMO or FMO.
"""
import argparse
import logging
from lib import my_env
from lib import murcsstore
from lib import murcsrest

ignore = my_env.solcomp_ignore
# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Set Transformation State for a solution component"
)
parser.add_argument('-a', '--solId', type=str, required=True,
                    help='Please provide solId for the solution Component.')
parser.add_argument('-e', '--env', type=str, required=True,
                    choices=['Production', 'Development', 'Quality', 'Other'],
                    help='Select environment (Production, Development, Quality, Other)')
parser.add_argument('-l', '--state', type=str, required=True,
                    choices=['Unknown', 'Open', 'In Progress', 'Transformed', 'Decommissioned'],
                    help='Please provide transformation state (Unknown, Open, In Progress, Transformed, '
                         'Decommissioned)')
args = parser.parse_args()
cfg = my_env.init_env("bellavista", __file__)
mdb = murcsstore.Murcs(cfg)
r = murcsrest.MurcsRest(cfg)
logging.info("Arguments: {a}".format(a=args))

solId = args.solId
sol_rec = mdb.get_sol(solId)
if not sol_rec:
    raise SystemExit("Solution {solId} not found.".format(solId=solId))
solInstId = my_env.get_solInstId(solId, args.env)
solInst_rec = mdb.get_solComp(solInstId)
solInstAttr_rec = mdb.get_sol_comp_rec(solInst_rec["id"])
if solInstAttr_rec:
    # Drop keys that are no longer required
    for k in ignore:
        del solInstAttr_rec[k]
    # Set State
    solInstAttr_rec["state"] = args.state
    solInstAttr_rec["solId"] = solId
    r.update_solution_component(solInstAttr_rec)
else:
    raise SystemExit("Solution Component {solInstId} for solution {solId} not found.".format(solInstId=solInstId,
                                                                                             solId=solId))
