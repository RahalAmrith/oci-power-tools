#########################################################################################
# Filename    : runner.py
# description : Wrapper that runs a tool and either lists or saves its DataFrame result
#########################################################################################

import pandas as pd
from tabulate import tabulate

from core.prompts import ToolAbort
from helpers.utils import SaveDataframeToReport

FILE_TYPES = [
    ("json", "JSON"),
    ("csv", "CSV"),
    ("excel", "Excel (.xlsx)"),
    ("html", "HTML (spreadsheet style web page)"),
]
MAX_TEXT_WIDTH = 60


def askOutputMode():
    while True:
        print("\nWhat do you want to do with the results?\n")
        print("\t1 : List in the terminal")
        print("\t2 : Save to a report file")

        mode = str(input("\nEnter option number : ")).strip()

        if mode in ("1", "2"):
            return "list" if mode == "1" else "save"

        print("Error : Invalid option")


def askFileDetails():
    fileName = str(input("\nEnter the File name : "))

    while True:
        print("\nSelect the output format :\n")

        for i, (_, label) in enumerate(FILE_TYPES):
            print(f"\t{i+1} : {label}")

        choice = str(input("\nEnter option number : ")).strip()

        if choice.isdigit() and 1 <= int(choice) <= len(FILE_TYPES):
            return fileName, FILE_TYPES[int(choice) - 1][0]

        print("Error : Invalid option")


def printDataframe(df):
    # Only wrap columns that hold sentences, so ids and names stay copyable
    widths = [
        MAX_TEXT_WIDTH if df[col].astype(str).str.contains(" ").any() else None
        for col in df.columns
    ]

    print(
        tabulate(
            df,
            headers="keys",
            tablefmt="rounded_grid",
            showindex=False,
            maxcolwidths=widths,
        )
    )


def removeTimezones(df):
    # Excel cannot store timezone aware datetimes
    df = df.copy()

    for col in df.columns:
        if isinstance(df[col].dtype, pd.DatetimeTZDtype):
            df[col] = df[col].dt.tz_convert("UTC").dt.tz_localize(None)

    return df


def runTool(tool, ctx):
    """tool is a function that takes the session and returns a pandas DataFrame."""

    mode = askOutputMode()

    try:
        df = tool(ctx)

    except ToolAbort as e:
        print(e)
        return

    except Exception as e:
        print("Error: {}".format(e))
        return

    if df is None or df.empty:
        print("\nNo results found.")
        return

    if mode == "list":
        print("")
        printDataframe(df)
        return

    fileName, fileType = askFileDetails()

    if fileType == "excel":
        df = removeTimezones(df)

    SaveDataframeToReport(dataFrame=df, fileName=fileName, fileType=fileType)
