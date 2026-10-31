#########################################################################################
# Filename    : user_events.py
# description : Audit - list the recent audit events performed by a user
#########################################################################################

from core.prompts import askIncludeReads, selectTimeWindow, selectUser
from tools.audit._common import (
    USER_EVENT_COLUMNS,
    explainNoMatch,
    fetchEvents,
    hideReads,
    selectCompartmentScope,
    selectRegions,
    toDataframe,
)


def run(ctx):
    user = selectUser(ctx)

    compartments = selectCompartmentScope(ctx)
    regions = selectRegions(ctx, compartments)
    start, end = selectTimeWindow()
    includeReads = askIncludeReads()

    fetched = fetchEvents(ctx, compartments, regions, start, end)
    events = fetched if includeReads else hideReads(fetched)

    events = [e for e in events if e["principal_id"] == user["id"]]

    if not events:
        print(f"\nLooking for principal id : {user['id']}")

        hidden = [e for e in fetched if e["principal_id"] == user["id"]]

        if hidden and not includeReads:
            print(
                f"Found {len(hidden)} events of this user, but all are read events. "
                "Answer y to include them."
            )
            return toDataframe([], USER_EVENT_COLUMNS)

        explainNoMatch(fetched, includeReads, f"user {user['name']}")

    return toDataframe(events, USER_EVENT_COLUMNS)
