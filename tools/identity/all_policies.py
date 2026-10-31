#########################################################################################
# Filename    : all_policies.py
# description : Identity - list the policy statements of every compartment
#########################################################################################

import pandas as pd

from tools.identity._common import policyStatements


def run(ctx):
    print("\nFetching Information")
    print("Please Wait. this may take some time\n")

    rows = [
        {"Compartment": cmpName, "Policy": polName, "Statement": st}
        for cmpName, polName, st in policyStatements(ctx)
    ]

    return pd.DataFrame(rows, columns=["Compartment", "Policy", "Statement"])
