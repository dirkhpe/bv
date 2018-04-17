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
    WHERE client.clientId="{clientId}"
      AND t1.softType="OperatingSystem";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)
    softId_arr = [rec["softId"] for rec in res]

    # Read the OS translation file
    os_filename = cfg["Main"]["translate"]
    df = pandas.read_excel(os_filename, sheet_name="os")
    my_loop = my_env.LoopInfo("OS Sync", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        softId = xl["softId"]
        if pandas.isnull(softId):
            break
        if softId not in softId_arr:
            logging.info("New OS found: {s}".format(s=softId))
            payload = dict(
                softwareId=xl["softId"],
                softwareName=xl["softName"],
                softwareVersion=xl["softVersion"],
                softwareType=xl["softType"],
                softwareSubType=xl["softSubType"],
                softwareVender=xl["softVendor"]
            )
            r.add_soft(softId, payload)

    my_loop.end_loop()
