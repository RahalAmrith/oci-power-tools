#########################################################################################
# Filename    : __init__.py
# description : Identity section - registry of the available tools
#########################################################################################

from tools.identity import (
    all_policies,
    groups,
    user_permissions,
    users_in_a_group,
    users_in_all_groups,
)

SECTION_NAME = "Identity"


def getTools():
    return [
        ("Groups", groups.run),
        ("Users in all groups", users_in_all_groups.run),
        ("Users in a group", users_in_a_group.run),
        ("All policies", all_policies.run),
        ("Permissions of a user", user_permissions.run),
    ]
