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
    lbl = "solutionContact"

    query = """
    SELECT sol.solId, sol.solName, role, firstName, lastName, email, person.company, title
    FROM contactpersonsol ps
    INNER JOIN sol ON sol.id=ps.solId
    INNER JOIN person ON person.id=ps.personId
    INNER JOIN client ON client.id=sol.clientId
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)

    xl = write2excel.Write2Excel()
    xl.init_sheet(lbl)
    xl.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "murcs_{lbl}.xlsx".format(lbl=lbl))
    xl.close_workbook(fn)
    mdb.close()
