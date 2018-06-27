"""
This script will find all virtual servers where Core is defined. The core property is removed.
For virtual servers only CPU count is listed. Core is not relevant for virtual servers.

The CPU field in MURCS for Virtual Servers is the 'Number of logical CPUs' in ESL (see ESL documentation).
A server with 4 CPU, 4 cores per CPU and Hyperthreading enabled has 4x4x2(hyperthreading) = 32 vCPUs.
"""
from lib import my_env
from lib import murcsrest, murcsstore

ignore = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "clientId", "siteId", "coreCount", "parentServer"]

if __name__ == "__main__":
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)

    # Get server records - procedure copy from extract_murcs\server.py
    # First get all field names for the table
    table = "server"
    field_array = mdb.get_fields(table)
    # Drop fields from array
    field_array.remove("parentServerId")
    field_array.remove("siteId")
    # Then add table identifier on field name
    fields_str = ", ".join(["t1.{f}".format(f=f) for f in field_array])

    # Add (lookup) fields
    add_fields_array = ["s2.hostName as parentServer", "site.siteId"]
    all_fields = ", ".join(add_fields_array)

    fields = fields_str + ", " + all_fields

    query = """
    SELECT {fields}
    FROM {table} t1
    LEFT JOIN server s2 ON s2.id = t1.parentServerId
    LEFT JOIN site ON site.id = t1.siteId
    INNER JOIN client ON client.id=t1.clientId
    WHERE client.clientId="{clientId}"
      AND t1.serverType = "VIRTUAL"
      AND t1.coreCount is not NULL;
    """.format(clientId=cfg["Murcs"]["clientId"], fields=fields, table=table)
    res = mdb.get_query(query)

    loop_info = my_env.LoopInfo("CoreCount", 20)
    for rec in res:
        serverId = rec["serverId"]
        payload = {}
        if rec["siteId"] is not None:
            payload["site"] = dict(siteId=rec["siteId"])
        if rec["parentServer"] is not None:
            payload["parentServer"] = dict(serverId=rec["parentServer"])
        for k in rec:
            # coreCount has been added to the ignore list so that it gets dropped.
            if (k not in ignore) and (rec[k] is not None):
                if k == "primaryIP":
                    payload["primaryIPAddress"] = rec[k]
                else:
                    payload[k] = rec[k]
        r.add_server(serverId=serverId, payload=payload)
        cnt = loop_info.info_loop()
        # if cnt > 3:
        #     break
    loop_info.end_loop()
    mdb.close()
