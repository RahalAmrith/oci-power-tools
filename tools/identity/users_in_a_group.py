#########################################################################################
# Filename    : users_in_a_group.py
# description : Identity - list the users of the groups matching a name
#########################################################################################

from tools.identity._common import usersInGroups


def run(ctx):
    search = str(input("\nEnter the group name : "))

    print("\nFetching Groups list")
    print("Please Wait. this may take some time\n")

    groupsList = ctx.ocisdk.getUserGroups(cfgName=ctx.profile)

    filteredGroupsList = [
        grp for grp in groupsList if search.lower() in str(grp["name"]).lower()
    ]

    print("")

    return usersInGroups(ctx, filteredGroupsList)
