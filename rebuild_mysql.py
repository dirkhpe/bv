"""
This procedure will rebuild the mysql BellaVista database
"""

import logging
from lib import my_env
from lib import localstore

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start application")
bv = localstore.mysqlUtils(cfg)
bv.rebuild()
logging.info("mysql bellavista rebuild")
logging.info("End application")
