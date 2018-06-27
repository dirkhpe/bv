"""
This script will try to load csv file with embedded newline characters.
"""
import argparse
import csv
import logging
import pandas
from lib import my_env
from lib import murcsrest
from lib import write2excel

if __name__ == "__main__":
    # Configure command line arguments
    parser = argparse.ArgumentParser(
        description="Load csv file with embedded newline characters"
    )
    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Please provide the file to load.')
    args = parser.parse_args()
    cfg = my_env.init_env("bellavista", __file__)
    r = murcsrest.MurcsRest(cfg)
    logging.info("Arguments: {a}".format(a=args))


    csv.register_dialect('tabdelim', delimiter='\t')
    with open(args.filename, newline='\r\n') as f:
        reader = csv.DictReader(f, dialect='tabdelim')
        xl = write2excel.Write2Excel()
        xl.init_sheet("VMData")
        xl.write_content(reader)
        fn = "c:/temp/vmdata.xlsx"
        xl.close_workbook(fn)

        # for row in reader:
        #     print(row[32])

    # Read the file
    """
    df = pandas.read_csv(args.filename, sep='\t', lineterminator=None)
    my_loop = my_env.LoopInfo("Servers", 20)
    for row in df.iterrows():
        my_loop.info_loop()
        # Get excel row in dict format
        xl = row[1].to_dict()
        clone = xl.pop("Clone Parent")
        if pandas.isnull(clone):
            print("Field Clone Parent not found")
        else:
            print(clone)
    my_loop.end_loop()
    """
