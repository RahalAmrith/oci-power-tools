#########################################################################################
# Filename    : groups.py
# description : Identity - list the groups of the tenancy
#########################################################################################

import pandas as pd


def run(ctx):
    groupsList = ctx.ocisdk.getUserGroups(cfgName=ctx.profile)

    return pd.DataFrame.from_dict(groupsList)
