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
    lbl = "person"

    # First get all field names for the table
    field_array = mdb.get_fields("person")
    fields = ", ".join(["t1.{f}".format(f=f) for f in field_array])

    query = """
    SELECT {fields}
    FROM person t1
    INNER JOIN client ON client.id=t1.clientId
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"], fields=fields)
    res = mdb.get_query(query)

    xl = write2excel.Write2Excel()
    xl.init_sheet(lbl)
    xl.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "murcs_{lbl}.xlsx".format(lbl=lbl))
    xl.close_workbook(fn)
    mdb.close()
