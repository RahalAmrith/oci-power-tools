#########################################################################################
# Filename    : user_permissions.py
# description : Identity - list the policy statements that apply to the groups of a user
#########################################################################################

import pandas as pd

from core.prompts import selectUser
from tools.identity._common import policyStatements


def run(ctx):
    user = selectUser(ctx)

    print("\nFetching Information")
    print("Please Wait. this may take some time\n")

    userGroupsList = ctx.ocisdk.getGroupsforUser(userId=user["id"], cfgName=ctx.profile)

    userGroupNameList = [grp["name"] for grp in userGroupsList]

    print("User is in following groups")
    for grp in userGroupNameList:
        print(f"\t{grp}")

    print("\n")

    rows = []

    for cmpName, polName, st in policyStatements(ctx):
        if "allow group" in str(st).lower() or "endorse group" in str(st).lower():

            for groupName in userGroupNameList:
                if groupName.lower() in str(st).lower():
                    rows.append(
                        {
                            "Compartment": cmpName,
                            "Group": groupName,
                            "Policy": polName,
                            "Statement": st,
                        }
                    )

    return pd.DataFrame(rows, columns=["Compartment", "Group", "Policy", "Statement"])
