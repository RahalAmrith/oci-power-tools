#########################################################################################
# Filename    : _common.py
# description : Logic shared by the identity tools
#########################################################################################

import pandas as pd

USER_IN_GROUP_COLUMNS = ["group_name", "group_id", "user_name", "user_id"]


def usersInGroups(ctx, groups):
    rows = []

    for group in groups:
        print(f"Fetching users in {group['name']}")
        usersList = ctx.ocisdk.getUsersInGroup(cfgName=ctx.profile, groupId=group["id"])

        for user in usersList:
            rows.append(
                {
                    "group_name": group["name"],
                    "group_id": group["id"],
                    "user_name": user["name"],
                    "user_id": user["id"],
                }
            )

    return pd.DataFrame(rows, columns=USER_IN_GROUP_COLUMNS)


def policyStatements(ctx):
    """Yields (compartment name, policy name, statement) for every policy in the tenancy."""

    compartments = ctx.ocisdk.getCompartments(cfgName=ctx.profile)

    for cmp in compartments.keys():
        policies = ctx.ocisdk.getAllPolicies(compartmentID=cmp, cfgName=ctx.profile)

        for pol in policies:
            for st in pol["statements"]:
                yield compartments[cmp]["name"], pol["name"], st
