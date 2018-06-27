"""
This script will create the FMO server to solution report. For every VPC server it will list all solutions attached to
it.
"""
import os
from lib import my_env
from lib import murcsstore
from lib import write2excel

if __name__ == "__main__":

    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    lbl = "server2solution"

    query = """
    SELECT distinct
           server.serverId, server.hostName, server.domain, server.hwModel, server.lifeCycleState,
           server.inScope as serverInScope, server.subCategory, server.service, server.supportGroup,
           CASE
               WHEN solinstcomponent.validFrom is NULL THEN 'not connected'
            ELSE 'FMO'
            END
           as mode,
           soft.softName, soft.softVersion, softinst.patchLevel,
           sol.solId, sol.solName, sol.inScope as applInScope, solinst.environment
    FROM server
    INNER JOIN client ON client.id=server.clientId
    INNER JOIN softinst ON server.id=softinst.serverId
    INNER JOIN soft ON softinst.softId=soft.id
    LEFT JOIN solinstcomponent ON solinstcomponent.softInstId=softinst.id
    LEFT JOIN solinst ON solinst.id=solinstcomponent.solInstId
    LEFT JOIN sol ON sol.id=solinst.solId
    WHERE client.clientId="{clientId}"
      AND server.serverId like "VPC.%";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)

    xls = write2excel.Write2Excel()
    xls.init_sheet(lbl)
    xls.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "report_{lbl}.xlsx".format(lbl=lbl))
    xls.close_workbook(fn)

    mdb.close()
