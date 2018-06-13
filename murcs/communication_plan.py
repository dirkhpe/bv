"""
This script will extract people data from communication plan and load it into murcs. People in roles for solutions
that are no longer listed in Murcs will be removed from the communication plan.

"""
import argparse
import logging
import pandas
import re
from lib import my_env
from lib import murcsrest
from lib import murcsstore


def add_people():
    """
    This method will add people to Murcs that are in communication plan but not yet in Murcs.

    :return:
    """
    logging.info("Review people to add to Murcs")
    dfp = df[["First name", "Last name", "E-mail"]].drop_duplicates()
    for prow in dfp.iterrows():
        xlr = prow[1].to_dict()
        mail = xlr["E-mail"]
        if pandas.notnull(mail):
            person_rec = mdb.get_person(mail)
            if not person_rec:
                payload = dict(email=mail)
                if pandas.notnull(xlr["First name"]):
                    payload["firstName"] = xlr["First name"]
                if pandas.notnull(xlr["Last name"]):
                    payload["lastName"] = xlr["Last name"]
                r.add_person(mail, payload)


def murcs_roles():
    """
    This method will collect all roles for people and solutions currently in MURCS.

    :return: list with  {solId}|{email}|{role} for each role.
    """
    # Collect contacts from Murcs
    query = """
    SELECT distinct contactpersonsol.role AS role, person.email AS email, sol.solId AS solId
    FROM contactpersonsol
    INNER JOIN person ON contactpersonsol.personId=person.id
    INNER JOIN client ON client.id=person.clientId
    INNER JOIN sol ON contactpersonsol.solId=sol.id
    WHERE client.clientId="{clientId}";
    """.format(clientId=cfg["Murcs"]["clientId"])
    res = mdb.get_query(query)
    roles = []
    for rec in res:
        contactId = "{solId}|{email}|{role}".format(solId=rec["solId"], email=rec["email"], role=rec["role"])
        roles.append(contactId)
    return roles


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
    add_people()
    # Collect contacts from MURCS. Add people/roles that are not in MURCS, remove people/roles in MURCS not in contact
    murcs_roles = murcs_roles()
    exc_roles = []
    p = re.compile("^\d{4}")
    my_loop = my_env.LoopInfo("Communication plan", 20)
    solId_arr = []
    for row in df.iterrows():
        my_loop.info_loop()
        xl = row[1].to_dict()
        email = xl["E-mail"]
        role = xl["Role"]
        if pandas.notnull(email) and pandas.notnull(role):
            app_list = xl["Application"]
            if pandas.notnull(app_list):
                for app in app_list.split(";"):
                    # Find Solution IDs in list column Application.
                    try:
                        solStr = p.search(app.strip()).group()
                    except AttributeError:
                        # SolID not found, ignore item in application list.
                        pass
                    else:
                        solId = int(solStr)
                        # Is this info in MURCS or is this new info?
                        contact_Id = "{solId}|{email}|{role}".format(solId=solId, email=email, role=role)
                        exc_roles.append(contact_Id)
                        if contact_Id not in murcs_roles:
                            # This is a new role for person and solution, add it to Murcs
                            if solId not in solId_arr:
                                sol_rec = mdb.get_sol(solId)
                                if sol_rec:
                                    solId_arr.append(solId)
                                else:
                                    logging.error("Could not find Solution with ID: {solId}".format(solId=solId))
                            if solId in solId_arr:
                                r.add_solution_contact(solId, email, role)
    my_loop.end_loop()

    # Now remove people in roles for solutions from Murcs that are no longer in the communication plan
    remove_contacts = [contact for contact in murcs_roles if contact not in exc_roles]
    for contact in remove_contacts:
        solId, email, role = contact.split("|")
        r.remove_solution_contact(solId, email, role)
    mdb.close()
