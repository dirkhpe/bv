"""
This script is a work-around for FMO Architecture. When reloading FMO servers, the solinstcomponent field validFrom is
reset to null.
This script will for all VPC servers collect the solinstcomponent records where the validFrom field is null, and set it
to the default FMO value. This should restore FMO configuration.
"""
from lib import my_env
from lib import murcsstore
from lib import murcsrest

if __name__ == "__main__":
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)

    query = """
    SELECT server.serverId AS serverId, softinst.instId AS softInstId, soft.softId AS softId,
           solinst.solInstId AS solInstId, sol.solId AS solId
    FROM server
    INNER JOIN client on server.clientId=client.id
    INNER JOIN softinst on softinst.serverID=server.id
    INNER JOIN soft on softinst.softId=soft.id
    INNER JOIN solinstcomponent on solinstcomponent.softInstId=softinst.id
    INNER JOIN solinst on solinstcomponent.solInstId=solinst.id
    INNER JOIN sol on solinst.solId=sol.id
    WHERE client.clientId = "{clientId}"
    AND server.hostname LIKE "VPC.%"
    AND solinstcomponent.validFrom is null
    """.format(clientId=cfg["Murcs"]["clientId"])

    res = mdb.get_query(query)
    mode = "FMO"
    for rec in res:
        serverId = rec["serverId"]
        softInstId = rec["softInstId"]
        softId = rec["softId"]
        solInstId = rec["solInstId"]
        solId = rec["solId"]
        r.add_solInstComp(solInstId, softInstId, solId, serverId, softId, mode)
    mdb.close()
