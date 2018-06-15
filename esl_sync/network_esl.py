"""
This script will sync MURCS IP addresses with ESL Report. It will load or update selected IP addresses VPC datacenter
into MURCS.
It will remove IP addresses from MURCS that are no longer in ESL.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest, murcsstore

dc_names = ["EMEA-DE-Frankfurt-eshelter-B"]
ip_labels = ["Primary IP", "auto detected - change"]

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Synchronize MURCS IP info with ESL information."
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file with ESL Server IP info..')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    src_name = "ESL"

    # Find Interface configs in ESL.
    net_in_murcs = []
    net_in_esl = []
    query = """
    SELECT distinct server.hostName as hostName, sni.netIfaceId
    FROM server
    INNER JOIN client on server.clientId=client.id
    INNER JOIN servernetiface sni on sni.serverId=server.id
    WHERE client.clientId = "{clientId}"
    AND server.hostName LIKE "VPC.%"
    AND sni.netIfaceId like "{src}|%"
    """.format(clientId=cfg["Murcs"]["clientId"], src=src_name)

    res = mdb.get_query(query)
    for rec in res:
        lbl = "{s}|{id}".format(s=rec["hostName"], id=rec["netIfaceId"])
        net_in_murcs.append(lbl)

    # Read the ESL report to load/update systems in MURCS.
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("ESL Interfaces", 20)
    for row in df.iterrows():
        # Get excel row in dict format
        xl = row[1].to_dict()
        # Only handle systems from VPC.
        if xl["DC Name"] in dc_names:
            lbl = xl["IP Type"]
            if lbl in ip_labels:
                my_loop.info_loop()
                serverId = my_env.fmo_serverId(xl["System Name"])
                ipAddress = xl["IP Address"]
                ifaceId = "{src}|{lbl}|{ip}".format(src=src_name, lbl=lbl, ip=ipAddress)
                srvlbl = "{s}|{id}".format(s=serverId, id=ifaceId)
                net_in_esl.append(srvlbl)
                if srvlbl not in net_in_murcs:
                    props = dict(
                        serverId=serverId,
                        networkInterfaceId=ifaceId,
                        interfaceName=lbl
                    )
                    if pandas.notnull(xl["MAC Address"]):
                        props["macAddress"] = xl["MAC Address"]
                    r.add_serverNetIface(serverId, ifaceId, props)
                    props = dict(
                        name=lbl
                    )
                    r.add_serverNetIfaceIp(serverId, ifaceId, ipAddress, props)
    my_loop.end_loop()

    lbls2remove = [lbl for lbl in net_in_murcs if lbl not in net_in_esl]
    for lbl in lbls2remove:
        serverId, source, lbl, ip = lbl.split("|")
        ifaceId = "{src}|{lbl}|{ip}".format(src=src_name, lbl=lbl, ip=ip)
        if source == src_name:
            if len(ip) > 4:
                r.remove_serverNetIfaceIp(serverId, ifaceId, ip)
            r.remove_serverNetIface(serverId, ifaceId)
