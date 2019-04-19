"""
This script will load person information.
"""
import logging
from lib import localstore
from lib import my_env
from lib.murcs import *
from lib import murcsrest

cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "person"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Persons", 20)
for trow in records:
    my_loop.info_loop()
    row = dict(trow)
    email = row.pop("email")
    payload = dict(
        email=email
    )
    for k in row:
        if row[k] and k not in excludedprops:
            payload[k] = row[k]
    r.add_person(email, payload)
cnt = my_loop.end_loop()
logging.info("End Application, {cnt} records processed.".format(cnt=cnt))
