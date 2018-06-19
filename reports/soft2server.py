"""
This script will create the software to server report. For every server the software will be listed.
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
    lbl = "soft2server"

    query = """
    SELECT distinct
           server.brand, server.category, server.domain, server.hostName, server.hwModel,
           server.inScope as serverInScope, server.serverId, server.subCategory, server.systemLocation,
           parent.hostName as parent, site.siteId as site, server.clockSpeedGhz, server.clusterName, server.coreCount,
           server.cpuCount, server.cpuType, server.lifeCycleState, server.memorySizeInByte as memSizeByte,
           softinst.instType, soft.softName, soft.softVersion, soft.softId
    FROM server
    INNER JOIN client ON client.id=server.clientId
    INNER JOIN softinst ON server.id=softinst.serverId
    LEFT JOIN server parent ON parent.id=server.parentServerId
    LEFT JOIN site ON server.siteId=site.id
    INNER JOIN soft ON softinst.softId=soft.id
    WHERE client.clientId="{clientId}"
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)

    xls = write2excel.Write2Excel()
    xls.init_sheet(lbl)
    xls.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "report_{lbl}.xlsx".format(lbl=lbl))
    xls.close_workbook(fn)

    mdb.close()
