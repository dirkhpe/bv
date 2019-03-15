"""
This script will load contact person per solution information.
"""
import logging
from lib import localstore
from lib import my_env
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "contactsolution"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Contact persons per solution", 20)
for trow in records:
    my_loop.info_loop()
    # Get excel row in dict format
    row = dict(trow)
    email = row.pop("email")
    role = row.pop("role")
    solId = row.pop("solutionId")
    r.add_solution_contact(solId, email, role)
my_loop.end_loop()
