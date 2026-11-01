#########################################################################################
# Filename    : _common.py
# description : Logic shared by the audit tools
#########################################################################################

import re
import threading
from concurrent.futures import ThreadPoolExecutor

import oci
import pandas as pd

from core.prompts import ToolAbort, selectCompartment

READ_ACTIONS = ("GET", "HEAD")
SEARCH_WORKERS = 5
OCID_PATTERN = re.compile(r"^ocid1\.[A-Za-z0-9._-]+$")

RESOURCE_EVENT_COLUMNS = [
    "time",
    "region",
    "event_name",
    "action",
    "status",
    "principal_name",
    "principal_id",
    "auth_type",
    "ip_address",
    "user_agent",
    "message",
    "resource_name",
    "resource_id",
    "compartment_name",
]

USER_EVENT_COLUMNS = [
    "time",
    "region",
    "event_name",
    "action",
    "status",
    "resource_name",
    "resource_id",
    "compartment_name",
    "auth_type",
    "ip_address",
    "user_agent",
    "message",
]


def selectCompartmentScope(ctx):
    """Returns None for the whole tenancy, or the one compartment the user picks."""

    print("\nSelect the compartments to search :\n")
    print("\t1 : All compartments")
    print("\t2 : One compartment")

    choice = str(input("\nEnter option number : ")).strip()

    if choice == "1":
        return None

    if choice == "2":
        return selectCompartment(ctx, includeRoot=True)

    raise ToolAbort("Invalid choice.")


def pickRegion(regions):
    for i, region in enumerate(regions):
        print(f"\t{i+1} - {region}")

    pick = str(input("Enter region number : ")).strip()

    if not pick.isdigit() or not 1 <= int(pick) <= len(regions):
        raise ToolAbort("Invalid choice.")

    return [regions[int(pick) - 1]]


def activeRegions(ctx, compartment):
    """Regions where the compartment (or the tenancy) had cost in the last 30 days.

    Returns [] when that cannot be found out.
    """

    print("\nFinding the regions in use (from the last 30 days of cost data)")

    compartmentId = compartment["id"] if compartment else None

    try:
        found = ctx.ocisdk.getCompartmentActiveRegions(
            compartmentID=compartmentId, cfgName=ctx.profile
        )

    except oci.exceptions.ServiceError as e:
        print(f"Could not read the cost data, {e.code} : {e.message}")
        return []

    return [item["region_name"] for item in found]


def regionOfOcid(ocid):
    """The region named in an ocid, None for a global resource.

    The region is written either as its name or as its short key, e.g. iad.
    """

    parts = ocid.split(".")

    if len(parts) < 4 or not parts[3]:
        return None

    return oci.regions.REGIONS_SHORT_NAMES.get(parts[3], parts[3])


def selectRegions(ctx, compartment=None, ocid=None):
    """Audit events are kept per region, so the regions to search have to be chosen.

    When the ocid names one of the subscribed regions (as a name or a key like iad)
    that region is used directly,
    otherwise the regions with cost in the compartment (or the tenancy) are used.
    """

    subscribed = ctx.ocisdk.getSubscribedRegions(cfgName=ctx.profile)

    region = regionOfOcid(ocid) if ocid else None

    if region in subscribed:
        print(f"The ocid belongs to the region {region}")
        return [region]

    print("\nSelect the regions to search :\n")
    print("\t1 : Regions in use (fast, based on cost data)")
    print("\t2 : One region I pick")

    choice = str(input("\nEnter option number : ")).strip()

    if choice == "2":
        return pickRegion(subscribed)

    if choice != "1":
        raise ToolAbort("Invalid choice.")

    regions = [r for r in activeRegions(ctx, compartment) if r in subscribed]

    if not regions:
        print("No region with cost found, please pick the region.\n")
        return pickRegion(subscribed)

    print(f"Regions in use : {', '.join(regions)}")
    print("Resources that cost nothing are not covered, pick the region to be sure.")

    return regions


def auditQuery(conditions, includeReads, compartment=None):
    """Logging search query over the audit logs of the whole tenancy.

    conditions are 'field = value' pairs that are all required to match.
    """

    where = [f"{field} = '{value}'" for field, value in conditions]

    if compartment:
        where.append(f"data.compartmentId = '{compartment['id']}'")

    if not includeReads:
        where.append(f"data.request.action not in {READ_ACTIONS}")

    return (
        f'search "{{tenancy}}/_Audit_Include_Subcompartment" '
        f"| where {' and '.join(where)} "
        "| sort by datetime desc"
    )


def fetchEvents(ctx, query, regions, start, end):
    """Audit events matching the query in the regions and time window, newest first.

    {tenancy} in the query is replaced by the tenancy of the profile. The regions are
    independent of each other, so they are searched side by side.
    """

    query = query.replace("{tenancy}", ctx.ocisdk.configs[ctx.profile]["tenancy"])

    progress = Progress(len(regions))

    def searchRegion(region):
        try:
            found = ctx.ocisdk.searchAuditLogs(
                query=query,
                startTime=start,
                endTime=end,
                cfgName=ctx.profile,
                region=region,
                onPage=progress.page,
            )

        # One region that cannot be searched should not lose the rest
        except oci.exceptions.ServiceError as e:
            progress.skipped(region, f"{e.code} : {e.message}")
            return []

        except oci.exceptions.RequestException as e:
            progress.skipped(region, f"no answer in time : {e}")
            return []

        progress.done()

        return [{**event, "region": region} for event in found]

    print(f"Searching audit logs in {len(regions)} region(s)")

    with ThreadPoolExecutor(max_workers=SEARCH_WORKERS) as pool:
        events = [e for found in pool.map(searchRegion, regions) for e in found]

    print()

    return sorted(events, key=lambda e: e["time"], reverse=True)


class Progress:
    """Shows how many regions are done and events found while a search runs."""

    def __init__(self, total):
        self.total = total
        self.finished = 0
        self.found = 0
        self.lock = threading.Lock()

    def show(self):
        print(
            f"\r\t{self.finished}/{self.total} regions done, "
            f"{self.found} events found ...",
            end="",
            flush=True,
        )

    def page(self, pageSize):
        with self.lock:
            self.found += pageSize
            self.show()

    def done(self):
        with self.lock:
            self.finished += 1
            self.show()

    def skipped(self, region, reason):
        with self.lock:
            self.finished += 1
            print(f"\r\t{region} skipped, {reason}" + " " * 20)
            self.show()


def explainNoMatch(regions, includeReads, what):
    print(f"\nNo events found for {what} in : {', '.join(regions)}.")

    if not includeReads:
        print("Read events were left out, answer y to include them.")

    print("Events are kept per region, so try the region the resource is in.")


def toDataframe(events, columns):
    return pd.DataFrame(events, columns=columns)
