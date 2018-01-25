"""
This procedure will rebuild the sqlite BellaVista database
"""

import logging
from lib import my_env
from lib import localstore

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start application")
bv = localstore.sqliteUtils(cfg)
bv.rebuild()
logging.info("sqlite bellavista rebuild")
logging.info("End application")
