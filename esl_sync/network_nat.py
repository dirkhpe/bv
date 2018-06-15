"""
This script will sync MURCS IP addresses with NAT Report.
It will remove IP addresses from MURCS that are no longer in NAT.
"""
import logging
import pandas
from lib import my_env
from lib import murcsrest, murcsstore

if __name__ == "__main__":
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)

    src_name = "NAT"

    # Find Interface configs in MURCS.
    net_in_murcs = []
    net_in_nat = []
    query = """
    SELECT distinct server.hostName as hostName, server.serverId as serverId, sni.netIfaceId
    FROM server
    INNER JOIN client on server.clientId=client.id
    INNER JOIN servernetiface sni on sni.serverId=server.id
    WHERE client.clientId = "{clientId}"
    AND sni.netIfaceId like "{src}|%"
    """.format(clientId=cfg["Murcs"]["clientId"], src=src_name)

    res = mdb.get_query(query)
    for rec in res:
        lbl = "{s}|{id}".format(s=rec["serverId"], id=rec["netIfaceId"])
        net_in_murcs.append(lbl)

    # Read the NAT report to load/update systems in MURCS.
    fn = cfg["Murcs"]["nat_ip"]
    df = pandas.read_excel(fn)
    my_loop = my_env.LoopInfo("NAT Interfaces", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        # Handle Caslano NAT
        srv_lbl = xl["SourceServer"].strip().lower()
        srv_rec = mdb.get_server(srv_lbl)
        if srv_rec:
            serverId = srv_rec["serverId"]
            lbl = "Caslano NAT"
            ip = xl[lbl].strip()
            ifaceId = "{src}|{lbl}|{ip}".format(src=src_name, lbl=lbl, ip=ip)
            srvlbl = "{s}|{id}".format(s=serverId, id=ifaceId)
            net_in_nat.append(srvlbl)
            if srvlbl not in net_in_murcs:
                props = dict(
                    serverId=serverId,
                    networkInterfaceId=ifaceId,
                    interfaceName=lbl
                )
                r.add_serverNetIface(serverId, ifaceId, props)
                props = dict(
                    name=lbl
                )
                r.add_serverNetIfaceIp(serverId, ifaceId, ip, props)
        else:
            logging.error("CMO Hostname {s} not found in MURCS".format(s=srv_lbl))
        # Handle VPC NAT
        srv_lbl = my_env.fmo_serverId(xl["TargetServer"])
        srv_rec = mdb.get_server(srv_lbl)
        if srv_rec:
            serverId = srv_rec["serverId"]
            lbl = "VPC NAT"
            ip = xl[lbl].strip()
            ifaceId = "{src}|{lbl}|{ip}".format(src=src_name, lbl=lbl, ip=ip)
            srvlbl = "{s}|{id}".format(s=serverId, id=ifaceId)
            net_in_nat.append(srvlbl)
            if srvlbl not in net_in_murcs:
                props = dict(
                    serverId=serverId,
                    networkInterfaceId=ifaceId,
                    interfaceName=lbl
                )
                r.add_serverNetIface(serverId, ifaceId, props)
                props = dict(
                    name=lbl
                )
                r.add_serverNetIfaceIp(serverId, ifaceId, ip, props)
        else:
            logging.error("FMO Hostname {s} not found in MURCS".format(s=srv_lbl))
    my_loop.end_loop()

    lbls2remove = [lbl for lbl in net_in_murcs if lbl not in net_in_nat]
    for lbl in lbls2remove:
        serverId, source, lbl, ip = lbl.split("|")
        ifaceId = "{src}|{lbl}|{ip}".format(src=src_name, lbl=lbl, ip=ip)
        if source == src_name:
            if len(ip) > 4:
                r.remove_serverNetIfaceIp(serverId, ifaceId, ip)
            r.remove_serverNetIface(serverId, ifaceId)
