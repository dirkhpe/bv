"""
In FMO, every software instance need to be linked to the solution component for the server.
This script will find all current server to solcomp relations. Then for every server, the script will verify if all
software instances are linked to the solution.
If not so, a link will be added.
"""
import logging
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)

    query = """
    SELECT server.serverId AS serverId, softinst.id AS softInst_id, soft.id AS soft_id,
           solinst.id AS solInst_id, sol.id AS sol_id
    FROM server
    INNER JOIN client on server.clientId=client.id
    INNER JOIN softinst on softinst.serverID=server.id
    INNER JOIN soft on softinst.softId=soft.id
    INNER JOIN solinstcomponent on solinstcomponent.softInstId=softinst.id
    INNER JOIN solinst on solinstcomponent.solInstId=solinst.id
    INNER JOIN sol on solinst.solId=sol.id
    WHERE client.clientId = "{clientId}"
    AND server.hostname LIKE "VPC.%"
    """.format(clientId=cfg["Murcs"]["clientId"])

    res = mdb.get_query(query)
    # Remember current server to solcomp links
    servers = []
    server_solcomp = {}
    server_solcomp_soft = {}
    for rec in res:
        serverId = rec["serverId"]
        server_id = rec["server_id"]
        softinst_id = rec["softInst_id"]
        solcomp_id = rec["solInst_id"]
        srv_sc_id = "{serverId}_{solcomp_id}".format(serverId=serverId, solcomp_id=solcomp_id)
        if serverId not in servers:
            servers.append(serverId)
            server_solcomp[serverId] = []
        if solcomp_id not in server_solcomp[serverId]:
            server_solcomp[serverId].append(solcomp_id)
            server_solcomp_soft[srv_sc_id] = []
        server_solcomp_soft[srv_sc_id].append(softinst_id)

    # Now find softinst attached to every server. Make sure every softinst is coupled with every solcomp for this
    # server.
    for serverId in servers:
        query = """
        SELECT softinst.id as softInst_id, softInst.instId as softInstId, soft.softId as softId
        FROM softinst
        INNER JOIN server ON server.id=softinst.serverId
        INNER JOIN client ON server.clientId=client.id
        INNER JOIN soft ON soft.id=softinst.softId
        WHERE client.clientId = "{clientId}"
          AND server.serverId = "{serverId}"
        """.format(clientId=cfg["Murcs"]["clientId"], serverId=serverId)
        res = mdb.get_query(query)
        for rec in res:
            softinst_id = rec["softInst_id"]
            # Verify that this softinst is linked to every solcomp
            for solcomp_id in server_solcomp[serverId]:
                srv_sc_id = "{serverId}_{solcomp_id}".format(serverId=serverId, solcomp_id=solcomp_id)
                if softinst_id not in server_solcomp_soft[srv_sc_id]:
                    # Get solcomp details
                    solInstId = mdb.get_name_id("solinst", "solInstId", solcomp_id)
                    solInst_rec = mdb.get_solComp(solInstId)
                    solId = solInst_rec["solId"]
                    softInstId = rec["softInstId"]
                    softId = rec["softId"]
                    logging.info("Link {serverId} to {solInstId} using software {softInstId}"
                                 .format(serverId=serverId, solInstId=solInstId, softInstId=softInstId))
                    r.add_solInstComp(solInstId, softInstId, solId, serverId, softId, "FMO")

    mdb.close()
