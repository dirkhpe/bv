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
    lbl = "solutionInstances"
    table = "solinst"

    # First get all field names for the table
    field_array = mdb.get_fields(table)
    # Drop fields from array
    field_array.remove("solId")
    # Then add table identifier on field name
    fields_str = ", ".join(["t1.{f}".format(f=f) for f in field_array])

    # Add (lookup) fields
    add_fields_array = ["sol.solId"]
    all_fields = ", ".join(add_fields_array)

    fields = fields_str + ", " + all_fields

    query = """
    SELECT {fields}
    FROM {table} t1
    INNER JOIN sol ON sol.id = t1.solId
    INNER JOIN client ON client.id=sol.clientId
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"], fields=fields, table=table)
    res = mdb.get_query(query)

    xl = write2excel.Write2Excel()
    xl.init_sheet(lbl)
    xl.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "murcs_{lbl}.xlsx".format(lbl=lbl))
    xl.close_workbook(fn)
    mdb.close()
