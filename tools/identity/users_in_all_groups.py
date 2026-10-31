#########################################################################################
# Filename    : users_in_all_groups.py
# description : Identity - list the users of every group
#########################################################################################

from tools.identity._common import usersInGroups


def run(ctx):
    print("\nPlease Wait. this may take some time\n")

    groupsList = ctx.ocisdk.getUserGroups(cfgName=ctx.profile)

    return usersInGroups(ctx, groupsList)
