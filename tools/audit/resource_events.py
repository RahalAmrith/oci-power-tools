#########################################################################################
# Filename    : resource_events.py
# description : Audit - list the audit events of a resource, found by its ocid
#########################################################################################

from core.prompts import ToolAbort, askIncludeReads, selectTimeWindow
from tools.audit._common import (
    OCID_PATTERN,
    RESOURCE_EVENT_COLUMNS,
    auditQuery,
    explainNoMatch,
    fetchEvents,
    selectRegions,
    toDataframe,
)


def run(ctx):
    resourceId = str(input("\nEnter the resource ocid : ")).strip()

    if not OCID_PATTERN.match(resourceId):
        raise ToolAbort("ERROR : That is not an ocid.")

    regions = selectRegions(ctx, ocid=resourceId)
    start, end = selectTimeWindow()
    includeReads = askIncludeReads()

    query = auditQuery([("data.resourceId", resourceId)], includeReads)
    events = fetchEvents(ctx, query, regions, start, end)

    if not events:
        explainNoMatch(regions, includeReads, "this resource")

    return toDataframe(events, RESOURCE_EVENT_COLUMNS)
