#########################################################################################
# Filename    : __init__.py
# description : Audit section - registry of the available tools
#########################################################################################

from tools.audit import resource_events, user_events

SECTION_NAME = "Audit"


def getTools():
    return [
        ("Audit events of a resource", resource_events.run),
        ("Audit events of a user", user_events.run),
    ]
