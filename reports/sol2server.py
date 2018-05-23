"""
This script will create the solution to server report. For every solution it will list all servers attached to it.
"""
import logging
import pandas
import os
from lib import my_env
from lib import murcsstore
from lib import write2excel

if __name__ == "__main__":

    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    lbl = "solution2server"

    query = """
    SELECT distinct
           sol.solId, sol.solName, sol.inScope as applInScope, sol.applicationTreatment, sol.applicationDetailTreatment,
           sol.customerBusinessUnit, sol.customerBusinessDivision, sol.supportBusinessUnit, sol.supportBusinessDivision,
           solinst.environment,
           server.brand, server.category, server.domain, server.hostName, server.hwModel,
           server.inScope as serverInScope, server.serverId, server.subCategory, server.systemLocation,
           parent.hostName as parent, site.siteId as site, server.clockSpeedGhz, server.clusterName, server.coreCount,
           server.cpuCount, server.cpuType, server.lifeCycleState, server.memorySizeInByte as memSizeByte,
           soft.softName, soft.softVersion
    FROM sol
    INNER JOIN client ON client.id=sol.clientId
    INNER JOIN solinst ON solinst.solId=sol.id
    INNER JOIN solinstcomponent ON solinstcomponent.solInstId=solinst.id
    INNER JOIN softinst ON solinstcomponent.softInstId=softinst.id
    INNER JOIN server ON server.id=softinst.serverId
    LEFT JOIN server parent ON parent.id=server.parentServerId
    LEFT JOIN site ON server.siteId=site.id
    LEFT JOIN softinst osinst ON osinst.serverId=server.id
    LEFT JOIN soft ON osinst.softId=soft.id
    WHERE client.clientId="{clientId}"
      AND osinst.instType="OperatingSystem";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)

    # Collect wave information per solution
    appsgroup_file = os.path.join(cfg["MurcsDump"]["dump_dir"], cfg["MurcsDump"]["appsgroup"])
    df = pandas.read_excel(appsgroup_file, sheet_name="applications")
    wave_d = {}
    servercnt = {}
    for row in df.iterrows():
        # Get excel row in dict format
        xl = row[1].to_dict()
        if pandas.notnull(xl["UniqueId"]):
            wave_d[str(xl["UniqueId"])] = xl["WAVE-GROUP"]
    # Then add wave information to application
    for rec in res:
        # Add wave to solution record
        try:
            rec["Wave"] = wave_d[str(rec["solId"])]
        except KeyError:
            logging.error("solId {solId} not in appslistconsolidated!".format(solId=rec["solId"]))
            rec["Wave"] = ""
        # Count servers per solution
        try:
            servercnt[str(rec["solId"])] += 1
        except KeyError:
            servercnt[str(rec["solId"])] = 1

    xls = write2excel.Write2Excel()
    xls.init_sheet(lbl)
    xls.write_content(res)

    # fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "report_{lbl}.xlsx".format(lbl=lbl))
    # xls.close_workbook(fn)

    # Create list of records with servercount per solution
    apps_summ = []
    for row in df.iterrows():
        # Get excel row in dict format
        xl = row[1].to_dict()
        if pandas.notnull(xl["UniqueId"]):
            wave_d[str(xl["UniqueId"])] = xl["WAVE-GROUP"]
            params = dict(
                solId=xl["UniqueId"],
                solName=xl["fullname"],
                wave=xl["WAVE-GROUP"]
            )
            try:
                params["servercount"] = servercnt[str(xl["UniqueId"])]
            except KeyError:
                params["servercount"] = 0
            apps_summ.append(params)
    xls.init_sheet("serversPerSol")
    xls.write_content(apps_summ)
    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "report_{lbl}.xlsx".format(lbl=lbl))
    xls.close_workbook(fn)

    mdb.close()
