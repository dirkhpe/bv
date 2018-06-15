"""
This script will load runbook information into MURCS.
"""
import argparse
import logging
import pandas
import re
from lib import my_env
from lib import murcsrest


def get_server_size(serverdesc):
    """
    This method will extract server size from server description.
    The server size is either in vCPUxMem or xvCPU, yGB.

    :param serverdesc:

    :return:
    """
    p1 = re.compile("\d+x\d+")  # Find 4x16
    p2 = re.compile("\d+vCPU")
    p3 = re.compile("\d+GB")
    # First try to find 4x16 pattern
    res = p1.findall(serverdesc)
    if len(res) == 1:
        size = res[0].split("x")
        ss = dict(
            core=size[0],
            mem=int(size[1])*1024*1024*1024
        )
        return ss
    elif len(res) > 1:
        logging.error("Multiple Server Sizes found {ss}".format(ss=res))
        return False
    # 4x16 pattern not found, find vCPU and GB
    corearr = p2.findall(serverdesc)
    memarr = p3.findall(serverdesc)
    if (len(corearr) == 1) and (len(memarr) == 1):
        ss = dict(
            core=corearr[0][:len(corearr[0])-len("vCPU")],
            mem=int(memarr[0][:len(memarr[0])-len("GB")])*1024*1024*1024
        )
        return ss
    else:
        logging.error("No server sizing found {str}".format(str=serverdesc))
        return False


def get_sla(serverdesc):
    """
    This method will extract sla from server description.
    The SLA is xx.x% SLA.

    :param serverdesc:

    :return: xx.x%
    """
    p = re.compile("\d\d.\d% SLA")
    res = p.findall(serverdesc)
    if len(res) == 1:
        v_sla = res[0][:len(res[0])-len(" SLA")]
        return v_sla
    elif len(res) > 1:
        logging.error("Multiple SLAs found {ss}".format(ss=res))
        return False
    else:
        logging.error("No SLA found {str}".format(str=serverdesc))
        return False


if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Load Runbook file into Murcs"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the runbook file to load.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Get BellaVista to softId translation for OS
    sw_tx = {}
    bv_tx_file = cfg["Main"]["translate"]
    df = pandas.read_excel(bv_tx_file, sheet_name="os")
    for row in df.iterrows():
        xl = row[1].to_dict()
        sw_tx[xl["BellaVistaOs"]] = xl["softId"]

    # Add BellaVista to softId translation
    df = pandas.read_excel(bv_tx_file, sheet_name="sw")
    for row in df.iterrows():
        xl = row[1].to_dict()
        sw_tx[xl["BellaVistaSw"]] = xl["softId"]

    # Read the runbook
    df = pandas.read_excel(args.filename, sheet_name="Server Order", header=1)
    my_loop = my_env.LoopInfo("Runbook", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        servername = xl.pop("Server Name")
        if pandas.isnull(servername):
            break

        # Add Server
        serverId = my_env.fmo_serverId(servername)
        payload = dict(
            serverId=serverId,
            hostName=serverId,
            category="Server",
            classification="Server",
            hwModel=xl["Server Sizing"].strip(),
            inScope="Yes",
            murcsScope="Unknown",
            site=dict(siteId="GE-VPC"),
            timeZone=xl["Time Zone"]
        )
        server_size = get_server_size(xl["Server Sizing"])
        if not server_size:
            logging.error("Server {s} could not extract Server Sizing {ss}".format(s=servername,
                                                                                   ss=xl["Server Sizing"]))
        else:
            payload["cpuCount"] = server_size["core"]
            payload["memorySizeInByte"] = server_size["mem"]
        sla = get_sla(xl["Server Sizing"])
        if sla:
            payload["sla"] = sla
        server_instance = xl.pop("Physical/ Virtual")
        if pandas.isnull(server_instance):
            logging.error("Server {s} empty instance (Physical/Virtual).".format(s=servername))
        elif server_instance in ["Physical", "Virtual"]:
            payload["serverType"] = server_instance.upper()
            payload["subCategory"] = server_instance
        else:
            logging.error("Server {s} unknown instance {i} (Physical/Virtual?)".format(s=servername, i=server_instance))
        # Server in DMZ?
        ifaceName = xl["VLAN"].strip()
        if "DMWeb" in ifaceName:
            payload["insideDMZ"] = "Yes"
        else:
            payload["insideDMZ"] = "No"
        r.add_server(serverId, payload)

        # Add Network Interface and IP Addresses
        r.add_serverNetIface(serverId, ifaceName)
        # Add "Net30 IP"
        ipAddress = xl["NET30 IP"]
        if pandas.notnull(ipAddress):
            payload = dict(ipAddressType="Net30 IP")
            r.add_serverNetIfaceIp(serverId, ifaceName, ipAddress, payload)
        # Add BYOIP
        ipAddress = xl["BYOIP"]
        if pandas.notnull(ipAddress):
            payload["ipAddressType"] = "BYOIP"
            r.add_serverNetIfaceIp(serverId, ifaceName, ipAddress, payload)
        # If available, add Public IP Address
        ipAddress = xl["Public IP"]
        if pandas.notnull(ipAddress):
            payload["ipAddressType"] = "Public IP"
            r.add_serverNetIfaceIp(serverId, ifaceName, ipAddress, payload)

        # Add OS
        # xl["OS"] should not be empty
        os = xl["OS"]
        try:
            softId = sw_tx[os.strip()]
        except KeyError:
            logging.error("OS Version {os} cannot be translated to softId".format(os=os))
        else:
            params = dict(
                instType='OperatingSystem'
            )
            r.add_softInst(softId, serverId, **params)

        # Add Database
        db = xl["Database Version"]
        if pandas.notnull(db):
            if db != "N/A":
                try:
                    softId = sw_tx[db.strip()]
                except KeyError:
                    logging.error("Database Version {db} cannot be translated to softId".format(db=db))
                else:
                    params = dict(
                        instType='Database'
                    )
                    r.add_softInst(softId, serverId, **params)

        # Add Phase as attribute
        phase = xl["Phase"]
        if pandas.notnull(phase):
            payload = dict(
                propertyName="phase",
                propertyValue=phase,
                description="Phase when server has been requested."
            )
            r.add_server_property(serverId, payload)

        # Add Environment as attribute
        env = xl["Environment"]
        if pandas.notnull(env):
            payload = dict(
                propertyName="Environment",
                propertyValue=env,
                description="Environment for the server."
            )
            r.add_server_property(serverId, payload)

    my_loop.end_loop()
