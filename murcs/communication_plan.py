"""
This script will extract people data from communication plan and load it into murcs.
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
        xl = prow[1].to_dict()
        email = xl["E-mail"]
        if pandas.notnull(email):
            person_rec = mdb.get_person(email)
            if not person_rec:
                payload = dict(email=email)
                if pandas.notnull(xl["First name"]):
                    payload["firstName"] = xl["First name"]
                if pandas.notnull(xl["Last name"]):
                    payload["lastName"] = xl["Last name"]
                r.add_person(email, payload)


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
                    try:
                        solStr = p.search(app.strip()).group()
                    except AttributeError:
                        pass
                    else:
                        solId = int(solStr)
                        if solId in solId_arr:
                            logging.debug("Another pass for solId  {solId}".format(solId=solId))
                            r.add_solution_contact(solId, email, role)
                        else:
                            sol_rec = mdb.get_sol(solId)
                            if sol_rec:
                                logging.debug("First pass for solId: {solId}".format(solId=solId))
                                solId_arr.append(solId)
                                r.add_solution_contact(solId, email, role)
                            else:
                                logging.error("Could not find Solution with ID: {solId}".format(solId=solId))
    my_loop.end_loop()
