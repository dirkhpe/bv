"""
This script will read the bv_translation.xlsx file, find new softId entries in os tab and create OS Software for
them.
It will read existing OS IDs in Murcs to guarantee that no duplicates are loaded.
"""
import logging
import pandas
from lib import my_env
from lib import murcsstore
from lib import murcsrest


def handle_tx_file(sheet):
    """
    This function will if all required SW or OS entries are loaded in MURCS. If not, a SW entry will be created.

    :param sheet: Name of the sheet to handle.
    :return:
    """
    df = pandas.read_excel(filename, sheet_name=sheet)
    my_loop = my_env.LoopInfo("{sheet} Sync".format(sheet=sheet), 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        softId = xl["softId"]
        if pandas.isnull(softId):
            break
        if softId not in softId_arr:
            logging.info("New {sheet} found: {s}".format(s=softId, sheet=sheet))
            payload = dict(
                softwareId=xl["softId"],
                softwareName=xl["softName"],
                softwareVersion=xl["softVersion"],
                softwareType=xl["softType"],
                softwareSubType=xl["softSubType"],
                softwareVendor=xl["softVendor"],
                inScope="Yes"
            )
            r.add_soft(softId, payload)
            softId_arr.append(softId)
    my_loop.end_loop()


if __name__ == "__main__":
    # Configure command line arguments
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)

    # Get SW IDs - Re-use query from extract_murcs\soft.py
    query = """
    SELECT softId
    FROM soft t1
    INNER JOIN client ON client.id=t1.clientId
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)
    softId_arr = [rec["softId"] for rec in res]

    # Read the OS translation file
    filename = cfg["Main"]["translate"]
    for sht in ["os", "sw"]:
        handle_tx_file(sht)
