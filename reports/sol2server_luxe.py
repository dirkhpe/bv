"""
This script will create the solution to server report. For every solution it will list all servers attached to it.

This luxe version collect Wave information and CR information from different sources.

appslistconsolidated.xlsx is the wave grouping for the common people, not for the luxury kind.
"""
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
           sol.solId, sol.solName, server.hostName
    FROM sol
    INNER JOIN client ON client.id=sol.clientId
    INNER JOIN solinst ON solinst.solId=sol.id
    INNER JOIN solinstcomponent ON solinstcomponent.solInstId=solinst.id
    INNER JOIN softinst ON solinstcomponent.softInstId=softinst.id
    INNER JOIN server ON server.id=softinst.serverId
    WHERE client.clientId="{clientId}"
    ORDER BY sol.solId, server.hostName;
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)

    # Collect CR information
    cr_file = cfg["SSoT"]["appscr"]
    df = pandas.read_excel(cr_file)
    cr_d = {}
    for row in df.iterrows():
        # Get excel row in dict format
        xl = row[1].to_dict()
        if pandas.notnull(xl["ID"]):
            cr_d[str(xl["ID"])] = xl
    # Collect wave information per solution
    appsgroup_file = cfg["SSoT"]["appsbaseline"]
    df = pandas.read_excel(appsgroup_file, sheet_name="full list")
    wave_d = {}
    for row in df.iterrows():
        # Get excel row in dict format
        xl = row[1].to_dict()
        if pandas.notnull(xl["Unique ID"]):
            wave_d[str(int(xl["Unique ID"]))] = xl

    # Then add wave information to application
    # Update to get servers on one line. Apps not in scope on separate sheets.
    servercnt = {}
    out_res = []
    not_in_scope_res = []
    # out_rec = {}
    prev_solID = ""
    all_solIds = []
    for rec in res:
        # Add wave to solution record
        solId = str(rec["solId"])
        if solId not in all_solIds:
            all_solIds.append(solId)
        try:
            hostName = rec["hostName"]
        except KeyError:
            hostName = ""
        if prev_solID != solId:
            # New record, remember previous one if there is one.
            if prev_solID:
                if out_rec["wave"] == "Appl not in full list":
                    not_in_scope_res.append(out_rec)
                else:
                    out_res.append(out_rec)
            prev_solID = solId
            # Create new record
            out_rec = {}
            try:
                out_rec["wave"] = wave_d[solId]["Wave"]
            except KeyError:
                out_rec["wave"] = "Appl not in full list"
            out_rec["solId"] = solId
            out_rec["solName"] = rec["solName"]
            try:
                out_rec["CR"] = cr_d[solId]["CR"]
            except KeyError:
                out_rec["CR"] = ""
            out_rec["hostName"] = hostName
        else:
            # Existing record, add hostName to hostName field.
            out_rec["hostName"] += "; {h}".format(h=hostName)
    # Also add last record.
    if out_rec["wave"] == "Appl not in full list":
        not_in_scope_res.append(out_rec)
    else:
        out_res.append(out_rec)

    # Add solutions from master list that do not have servers attached to it
    for solId in wave_d:
        if solId not in all_solIds:
            # I found a solution without servers
            out_rec = dict(
                wave=wave_d[solId]["Wave"],
                solId=solId,
                solName=wave_d[solId]["Application Name"]
            )
            try:
                out_rec["CR"] = cr_d[solId]["CR"]
            except KeyError:
                out_rec["CR"] = ""
            out_rec["hostName"] = ""
            out_res.append(out_rec)

    xls = write2excel.Write2Excel()
    xls.init_sheet(lbl)
    xls.write_content(out_res)

    xls.init_sheet("Sol Not in Scope")
    xls.write_content(not_in_scope_res)

    fn = os.path.join(cfg["MurcsDump"]["dump_dir"], "report_{lbl}_ext.xlsx".format(lbl=lbl))
    xls.close_workbook(fn)

    mdb.close()
