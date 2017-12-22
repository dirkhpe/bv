"""
This script will collect all solution data from bellavista excel and load it in Neo4J database.
"""

import logging

from lib import my_env
from lib.neostore import NeoStore
from lib import localstore
from lib.localstore import *


nodes = {}
rels = []


def handle_relation(from_node, from_key, to_node, to_key, reltype):
    """
    This method will check if a directional relation does exist already.
    If not, it will be created.

    :param from_node:

    :param from_key:

    :param to_node:

    :param to_key:

    :param reltype:

    :return:
    """
    rel_key = "{f} {t}".format(f=from_key, t=to_key)
    logging.debug("Relation key: {rk}".format(rk=rel_key))
    if rel_key not in rels:
        # Relation does not exist, create it
        ns.create_relation(from_node, reltype, to_node)
        # Remember that the relation does exist
        rels.append(rel_key)
    return


def handle_node(node_name, node_label, **node_attribs):
    """
    This method will handle a node. It will get a node name and label. If the node does not exist yet, it will be
    created.
    The node is returned to the calling application.
    If name is not defined, then FALSE is returned

    :param node_name:

    :param node_label:

    :return: The Neo4J node - or False if name is not defined.
    """
    if node_name:
        # node_key = "{l} {n}".format(l=node_label, n=node_name)
        node_key = "{n}".format(n=node_name)
        try:
            return nodes[node_key]
        except KeyError:
            # building node does not exist, create one
            nodes[node_key] = ns.create_node(node_label, **node_attribs)
        return nodes[node_key]
    else:
        return False


if __name__ == "__main__":
    cfg = my_env.init_env("bellavista", __file__)
    logging.getLogger('neo4j.bolt').setLevel(logging.WARNING)
    logging.info("Start Application")
    # Get Neo4J Connection and clean Database
    ns = NeoStore(cfg, refresh="No")
    db = cfg['Main']['db']
    ds, engine = localstore.init_session(db=db)
    # get solution information
    solutions = ds.query(Solution)
    loop = my_env.LoopInfo("Solutions", 25)
    for rec in solutions:
        loop.info_loop()
        attribs = {}
        for col in Solution.__table__.columns.keys():
            if getattr(rec, col):
                attribs[col] = getattr(rec, col)
        handle_node(attribs["solId"], "Solution", **attribs)
    loop.end_loop()

    # get relation information
    sol2sols = ds.query(SolutionToSolution)
    loop = my_env.LoopInfo("Relations", 25)
    for rec in sol2sols:
        loop.info_loop()
        attribs = {}
        for col in SolutionToSolution.__table__.columns.keys():
            if getattr(rec, col):
                attribs[col] = getattr(rec, col)
        if 'member' in attribs["comment"]:
            relType = 'member'
            handle_relation(nodes[attribs["toSolId"]], attribs["toSolId"],
                            nodes[attribs["fromSolId"]], attribs["fromSolId"], relType)
        else:
            relType = 'to'
            handle_relation(nodes[attribs["fromSolId"]], attribs["fromSolId"],
                            nodes[attribs["toSolId"]], attribs["toSolId"], relType)
    logging.info('End Application')
