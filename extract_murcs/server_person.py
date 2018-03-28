"""
This script will extract Person to solution.
"""
import os
from lib import my_env
from lib import murcsstore
from lib import write2excel

if __name__ == "__main__":

    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    lbl = "serverContact"

    query = """
    SELECT server.serverId, server.hostName, role, firstName, lastName, email, person.company, title
    FROM contactpersonserver ps
    INNER JOIN server ON server.id=ps.serverId
    INNER JOIN person ON person.id=ps.personId
    INNER JOIN client ON client.id=server.clientId
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)

    xl = write2excel.Write2Excel()
    xl.init_sheet(lbl)
    xl.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "murcs_{lbl}.xlsx".format(lbl=lbl))
    xl.close_workbook(fn)
    mdb.close()
