#########################################################################################
# Filename    : vms_by_tag.py
# description : Virtual Machines - list the VMs having a given tag value
#########################################################################################

import pandas as pd

from core.prompts import selectCompartment


def run(ctx):
    compartment = selectCompartment(ctx)

    tagKey = str(input("Enter the tag key to filter by : "))
    tagValue = str(input("Enter the tag value to filter by (Enter comma seperated) : "))

    vmList = ctx.ocisdk.getAllVMsByTag(
        compartmentID=compartment["id"],
        tagKey=tagKey,
        tagValue=tagValue,
        cfgName=ctx.profile,
    )

    return pd.DataFrame.from_dict(vmList)
