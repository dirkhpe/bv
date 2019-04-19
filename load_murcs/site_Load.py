"""
This script will load a site file.
"""
import logging
from lib import localstore
from lib import my_env
from lib import murcsrest


cfg = my_env.init_env("bellavista", __file__)
r = murcsrest.MurcsRest(cfg)
lcl = localstore.sqliteUtils(cfg)
tablename = "site"
logging.info("Handling table: {t}".format(t=tablename))

records = lcl.get_table(tablename)
my_loop = my_env.LoopInfo("Sites", 20)
for trow in records:
    row = dict(trow)
    my_loop.info_loop()
    siteId = row.pop("siteId")
    payload = dict(
        siteId=siteId
    )
    for k in row:
        if row[k]:
            payload[k] = row[k]
    r.add_site(siteId, payload)
cnt = my_loop.end_loop()
logging.info("End Application, {cnt} records processed.".format(cnt=cnt))
