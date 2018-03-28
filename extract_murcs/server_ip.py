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
    lbl = "server_net_ip"
    t1 = "servernetifaceip"
    t2 = "servernetiface"

    # First get all field names for the table servernetifaceip
    field_array = mdb.get_fields(t1)
    # Drop fields from array
    field_array.remove("serverNetIfaceId")
    # Then add table identifier on field name
    fields_str_1 = ", ".join(["t1.{f}".format(f=f) for f in field_array])

    # Then get all field names for table servernetiface
    field_array = mdb.get_fields(t2)
    # Drop fields from array
    field_array.remove("serverId")
    for f in ["id", "changedAt", "changedBy", "createdAt", "createdBy"]:
        field_array.remove(f)
        # Then add table identifier on field name
    fields_str_2 = ", ".join(["t2.{f}".format(f=f) for f in field_array])

    # Add (lookup) fields
    add_fields_array = ["server.serverId"]
    all_fields = ", ".join(add_fields_array)

    fields = fields_str_1 + ", " + fields_str_2 + ", " + all_fields

    query = """
    SELECT {fields}
    FROM {t1} t1
    INNER JOIN {t2} t2 ON t2.id = t1.serverNetIfaceId
    INNER JOIN server ON server.id = t2.serverId
    INNER JOIN client ON client.id=server.clientId
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"], fields=fields, t1=t1, t2=t2)
    res = mdb.get_query(query)

    xl = write2excel.Write2Excel()
    xl.init_sheet(lbl)
    xl.write_content(res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "murcs_{lbl}.xlsx".format(lbl=lbl))
    xl.close_workbook(fn)
    mdb.close()
