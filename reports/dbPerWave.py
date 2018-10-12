"""
This script will list the databases per wave - allowing for Peter to plan for the DB resources.

The soft2server report will be read to understand servers with databases. This info is then attached to the master wave
planning.

"""

import argparse
import logging
import os
import pandas
from lib import my_env
from lib import write2excel


db_names = ["Oracle DB", "MSSQL DB", "DB2", "PostgreSQL", "MySQL DB"]
dbs = {}

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Solution - Wave Plan"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the solution-wave plan file to load.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    logging.info("Arguments: {a}".format(a=args))

    # Get latest wave to solution link.
    fn = args.filename
    df = pandas.read_excel(args.filename, "full list")
    waves = {}
    for row in df.iterrows():
        xl = row[1].to_dict()
        solid = xl["Unique ID"]
        if pandas.notnull(solid):
            waves[str(int(solid))] = xl["Wave"]

    # Initialize dbs - resulthash
    for db in db_names:
        dbs[db] = []
    # Get soft2server location.
    report_dir = cfg["MurcsDump"]["dump_dir"]
    fn = os.path.join(report_dir, "report_{lbl}.xlsx".format(lbl="soft2server"))
    df = pandas.read_excel(fn, "soft2server")
    # For every database type, collect servers
    for row in df.iterrows():
        xl = row[1].to_dict()
        softName = xl["softName"]
        if softName in db_names:
            # Server with database found.
            serverId = xl["serverId"]
            # Add server to dbs array for db if not already there
            if __name__ == '__main__':
                if serverId not in dbs[softName]:
                    dbs[softName].append(serverId)


    # Now read all solution to server information, to add database information to it
    fn = os.path.join(report_dir, "report_{lbl}.xlsx".format(lbl="solution2server"))
    df = pandas.read_excel(fn, "solution2server")
    res = []
    for row in df.iterrows():
        xl = row[1].to_dict()
        solId = str(xl["solId"])
        if solId in waves:
            rec = dict(
                wave=waves[solId],
                solId=solId,
                solName=xl["solName"],
                hostName=xl["hostName"]
            )
            serverId = xl["serverId"]
            for db in dbs:
                if serverId in dbs[db]:
                    rec[db] = db
                else:
                    rec[db] = ""
            res.append(rec)

    lbl = "dbPerApp"
    xls = write2excel.Write2Excel()
    xls.init_sheet(lbl)
    xls.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "report_{lbl}.xlsx".format(lbl=lbl))
    xls.close_workbook(fn)
