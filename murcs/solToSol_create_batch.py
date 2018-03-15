"""
This script will create solution to solution links from a file.
"""
import argparse
import logging
import pandas
from lib import my_env
from lib import murcsrest

tx = {"Topic Interface": "description",
      "Direction": "connectionDirection",
      "Calls": "connectionType",
      "Frequency": "connectionFrequency",
      "Remarks": "comment",
      "Technology": "connectionSubType"}

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Create Solution to Solution links"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file containing the solution to solution information.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))

    # Read the file
    df = pandas.read_excel(args.filename)
    my_loop = my_env.LoopInfo("solToSol", 20)
    cnt = 0
    for row in df.iterrows():
        cnt += 1
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        fromSolId = xl.pop("source_id")
        toSolId = xl.pop("target_id")
        solToSolId = "{fromSolId}_{toSolId}_{cnt}".format(fromSolId=fromSolId, toSolId=toSolId, cnt=cnt)
        payload = {}
        for k in tx:
            v = xl.pop(k)
            if pandas.notnull(v):
                payload[tx[k]] = v
        payload["solutionToSolutionId"] = solToSolId
        r.add_solToSol(solToSolId, fromSolId, toSolId, payload)
    my_loop.end_loop()
