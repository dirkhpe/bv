"""
This script will synchronize Murcs with information from communication plan. Contacts that are in MURCS but not in
communication plan will be removed.
"""
import argparse
import logging
import pandas
import re
from lib import my_env
from lib import murcsrest
from lib import murcsstore


if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Communication plan extract people for loading into Murcs"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the communication plan file to load.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    mdb = murcsstore.Murcs(cfg)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    df = pandas.read_excel(args.filename, "Participants")
    p = re.compile("^\d{4}")
    my_loop = my_env.LoopInfo("Communication plan", 20)
    contacts = []
    for row in df.iterrows():
        my_loop.info_loop()
        xl = row[1].to_dict()
        email = xl["E-mail"]
        role = xl["Role"]
        if pandas.notnull(email) and pandas.notnull(role):
            app_list = xl["Application"]
            if pandas.notnull(app_list):
                for app in app_list.split(";"):
                    try:
                        solStr = p.search(app.strip()).group()
                    except AttributeError:
                        pass
                    else:
                        solId = int(solStr)  # Remove leading 0 from solId
                        contactId = "{solId}|{email}|{role}".format(solId=solId, email=email, role=role).lower()
                        if contactId not in contacts:
                            contacts.append(contactId)
    my_loop.end_loop()

    # Collect contacts from Murcs
    query = """
    SELECT contactpersonsol.role AS role, person.email AS email, sol.solId AS solId
    FROM contactpersonsol
    INNER JOIN person ON contactpersonsol.personId=person.id
    INNER JOIN client ON client.id=person.clientId
    INNER JOIN sol ON contactpersonsol.solId=sol.id
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)
    cnt = 0
    for rec in res:
        contactId = "{solId}|{email}|{role}".format(solId=rec["solId"], email=rec["email"], role=rec["role"])
        if contactId.lower() not in contacts:
            r.remove_solution_contact(rec["solId"], rec["email"], rec["role"])
    mdb.close()
