#########################################################################################
# Filename    : resource_events.py
# description : Audit - list the audit events of a resource, found by its ocid
#########################################################################################

from core.prompts import (
    ToolAbort,
    askIncludeReads,
    selectCompartment,
    selectTimeWindow,
)
from tools.audit._common import (
    RESOURCE_EVENT_COLUMNS,
    explainNoMatch,
    fetchEvents,
    hideReads,
    selectRegions,
    toDataframe,
)


def run(ctx):
    resourceId = str(input("\nEnter the resource ocid : ")).strip()

    if not resourceId.startswith("ocid1."):
        raise ToolAbort("ERROR : That is not an ocid.")

    compartment = selectCompartment(ctx, includeRoot=True)
    regions = selectRegions(ctx, [compartment], ocid=resourceId)
    start, end = selectTimeWindow()
    includeReads = askIncludeReads()

    fetched = fetchEvents(ctx, [compartment], regions, start, end)
    events = fetched if includeReads else hideReads(fetched)

    # The ocid is also checked in the request path, some events (e.g. updates of a
    # child object) carry the parent ocid there and not in the resource id
    events = [
        e
        for e in events
        if e["resource_id"] == resourceId or resourceId in str(e["path"])
    ]

    if not events:
        explainNoMatch(fetched, includeReads, "this resource")

    return toDataframe(events, RESOURCE_EVENT_COLUMNS)
