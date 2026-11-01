#########################################################################################
# Filename    : user_events.py
# description : Audit - list the recent audit events performed by a user
#########################################################################################

from core.prompts import askIncludeReads, selectTimeWindow, selectUser
from tools.audit._common import (
    USER_EVENT_COLUMNS,
    auditQuery,
    explainNoMatch,
    fetchEvents,
    selectCompartmentScope,
    selectRegions,
    toDataframe,
)


def run(ctx):
    user = selectUser(ctx)

    compartment = selectCompartmentScope(ctx)
    regions = selectRegions(ctx, compartment)
    start, end = selectTimeWindow()
    includeReads = askIncludeReads()

    query = auditQuery(
        [("data.identity.principalId", user["id"])], includeReads, compartment
    )
    events = fetchEvents(ctx, query, regions, start, end)

    if not events:
        print(f"\nLooking for principal id : {user['id']}")
        explainNoMatch(regions, includeReads, f"user {user['name']}")

    return toDataframe(events, USER_EVENT_COLUMNS)
