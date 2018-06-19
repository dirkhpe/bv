"""
This script will sync MURCS Servers with ESL Report. It will load or update all servers in VPC datacenter into MURCS.
A list of servers in MURCS but no longer in VPC will be created.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest, murcsstore

dc_names = ["EMEA-DE-Frankfurt-eshelter-B"]
ignore = ["id", "changedAt", "changedBy", "createdAt", "createdBy", "clientId"]

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Synchronize MURCS Servers with ESL information."
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file with ESL Server info..')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Get BellaVista to softId translation for OS
    sw_tx = {}
    bv_tx_file = cfg["Main"]["translate"]
    df = pandas.read_excel(bv_tx_file, sheet_name="os")
    for row in df.iterrows():
        xl = row[1].to_dict()
        sw_tx[xl["BellaVistaOs"]] = xl["softId"]

    # Get MURCS - ESL mapping
    m2e = {}
    m2e_fixed = {}
    m2e_file = cfg["Murcs"]["murcs2esl_server"]
    df = pandas.read_excel(m2e_file)
    for row in df.iterrows():
        xl = row[1].to_dict()
        if pandas.notnull(xl["esl"]):
            m2e[xl["murcs"]] = xl["esl"]
        elif pandas.notnull(xl["fixed"]):
            m2e_fixed[xl["murcs"]] = xl["fixed"]

    srv_in_esl = []
    # Read the ESL report to load/update systems in MURCS.
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("ESL", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        # Only handle systems from VPC.
        if xl["DC Name"] in dc_names:
            host = my_env.fmo_serverId(xl["System Name"])
            srv_in_esl.append(host)
            # Create dictionary with info from ESL
            serverprops = dict(
                hostName=host,
                serverId=host,
                site=dict(siteId=xl["DC Name"])
            )
            # Add fixed strings to dictionary
            for k in m2e_fixed:
                serverprops[k] = m2e_fixed[k]
            # Add variable ESL information to dictionary
            for k in m2e:
                if pandas.notnull(xl[m2e[k]]):
                    if k == "domain":
                        # Remove host from fqdn to get domain
                        fqdn = xl[m2e[k]]
                        serverprops[k] = fqdn[fqdn.index(".")+1:]
                    elif k == "memorySizeInByte":
                        serverprops[k] = xl[m2e[k]] * 1024 * 1024
                    elif k == "clockSpeedGhz":
                        serverprops[k] = xl[m2e[k]] / 1000
                    else:
                        serverprops[k] = xl[m2e[k]]
                    # if null then k will not be added to serverprops so value in Murcs will be set to blank
            # Check for update or new record
            server_rec = mdb.get_server(host)
            if server_rec:
                # Remember softId for OS
                soft_rec = mdb.get_softInst_os(host)
                os_id = "to be defined"
                if soft_rec:
                    os_id = soft_rec["softId"]
                else:
                    del os_id
                # Update existing server record
                for k in server_rec:
                    if not ((k in ignore) or (k in m2e) or (k in m2e_fixed)):
                        if pandas.notnull(server_rec[k]):
                            serverprops[k] = server_rec[k]
            r.add_server(host, serverprops)

            # Add OS if new or Update compared to previous version
            os = xl["OS Version"]
            try:
                softId = sw_tx[os.strip()]
            except KeyError:
                logging.error("OS Version {os} cannot be translated to softId".format(os=os))
            else:
                # Check if this is update OS or new OS definition. Don't update if OK already
                try:
                    if os_id != softId:
                        logging.info("Server {h} new OS {s} (from {o})".format(h=host, s=softId, o=os_id))
                        params = dict(
                            instType='OperatingSystem'
                        )
                        r.add_softInst(softId, host, **params)
                except NameError:
                    # No OS found for this server in MURCS
                    params = dict(
                        instType='OperatingSystem'
                    )
                    r.add_softInst(softId, host, **params)
    my_loop.end_loop()

    # Now find servers in MURCS that are not in ESL.
    query = """
    SELECT server.hostName as hostName
    FROM server
    INNER JOIN client on server.clientId=client.id
    WHERE client.clientId = "{clientId}"
    AND server.hostName LIKE "VPC.%"
    """.format(clientId=cfg["Murcs"]["clientId"])

    res = mdb.get_query(query)
    for rec in res:
        if rec["hostName"] not in srv_in_esl:
            logging.error("Server {h} in MURCS, not in ESL.".format(h=rec["hostName"]))
