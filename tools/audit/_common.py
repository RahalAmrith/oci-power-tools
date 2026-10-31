#########################################################################################
# Filename    : _common.py
# description : Logic shared by the audit tools
#########################################################################################

import threading

import oci
import pandas as pd

from core.prompts import ToolAbort, selectCompartment

READ_ACTIONS = ("GET", "HEAD")

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
    """Returns the compartments to scan, the whole tenancy or the one the user picks."""

    print("\nSelect the compartments to scan :\n")
    print("\t1 : All compartments (complete, but slow on a large tenancy)")
    print("\t2 : One compartment")

    choice = str(input("\nEnter option number : ")).strip()

    if choice == "1":
        compartments = ctx.ocisdk.getCompartments(cfgName=ctx.profile)

        return [
            {"id": cmpId, "name": cmp["name"]} for cmpId, cmp in compartments.items()
        ]

    if choice == "2":
        return [selectCompartment(ctx, includeRoot=True)]

    raise ToolAbort("Invalid choice.")


def pickRegion(regions):
    for i, region in enumerate(regions):
        print(f"\t{i+1} - {region}")

    pick = str(input("Enter region number : ")).strip()

    if not pick.isdigit() or not 1 <= int(pick) <= len(regions):
        raise ToolAbort("Invalid choice.")

    return [regions[int(pick) - 1]]


def activeRegions(ctx, compartments):
    """Regions where the compartments had cost in the last 30 days, [] when unknown."""

    print("\nFinding the regions in use (from the last 30 days of cost data)")

    try:
        if len(compartments) == 1:
            found = ctx.ocisdk.getCompartmentActiveRegions(
                compartmentID=compartments[0]["id"], cfgName=ctx.profile
            )
        else:
            found = ctx.ocisdk.getCompartmentActiveRegions(cfgName=ctx.profile)

    except oci.exceptions.ServiceError as e:
        print(f"Could not read the cost data, {e.code} : {e.message}")
        return []

    return [item["region_name"] for item in found]


def selectRegions(ctx, compartments, ocid=None):
    """Audit events are kept per region, so the regions to search have to be chosen.

    When the ocid names one of the subscribed regions that region is used directly,
    otherwise the regions with cost in the compartments are used.
    """

    subscribed = ctx.ocisdk.getSubscribedRegions(cfgName=ctx.profile)

    if ocid:
        for region in subscribed:
            if f".{region}." in ocid:
                print(f"The ocid belongs to the region {region}")
                return [region]

    print("\nSelect the regions to search :\n")
    print("\t1 : Regions in use by the compartments (fast, based on cost data)")
    print("\t2 : One region I pick")

    choice = str(input("\nEnter option number : ")).strip()

    if choice == "2":
        return pickRegion(subscribed)

    if choice != "1":
        raise ToolAbort("Invalid choice.")

    regions = [r for r in activeRegions(ctx, compartments) if r in subscribed]

    if not regions:
        print("No region with cost found, please pick the region.\n")
        return pickRegion(subscribed)

    print(f"Regions in use : {', '.join(regions)}")
    print("Resources that cost nothing are not covered, pick the region to be sure.")

    return regions


def fetchEvents(ctx, compartments, regions, start, end):
    """Audit events of the compartments in the regions and time window, newest first."""

    events = []
    total = len(compartments) * len(regions)
    done = 0

    for region in regions:
        for cmp in compartments:
            done += 1
            print(f"Fetching audit events ({done}/{total}) : {region} / {cmp['name']}")

            counter = PageCounter()

            try:
                found = ctx.ocisdk.getAuditEvents(
                    compartmentID=cmp["id"],
                    startTime=start,
                    endTime=end,
                    cfgName=ctx.profile,
                    region=region,
                    onPage=counter.add,
                )

            except oci.exceptions.ServiceError as e:
                # One compartment the user cannot read should not lose the rest
                print(f"\n\tSkipped, {e.code} : {e.message}")
                continue

            print(f"\r\t{len(found)} events fetched" + " " * 10)

            events.extend({**event, "region": region} for event in found)

    return sorted(events, key=lambda e: e["time"], reverse=True)


class PageCounter:
    """Shows how many events were fetched so far, a busy compartment takes a while."""

    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def add(self, pageSize):
        with self.lock:
            self.count += pageSize
            print(f"\r\t{self.count} events fetched ...", end="", flush=True)


def hideReads(events):
    return [e for e in events if e["action"] not in READ_ACTIONS]


def explainNoMatch(fetched, includeReads, what):
    """Tells why nothing matched, so an empty result can be told apart from a miss."""

    reads = len(fetched) - len(hideReads(fetched))

    print(f"\nFetched {len(fetched)} audit events ({reads} reads), none match {what}.")

    if not fetched:
        print("OCI returned no events for the compartments and time window selected.")
        return

    if reads and not includeReads:
        print(f"{reads} read events were hidden, answer y to include them.")

    print("\nMost active principals in what was fetched :\n")

    counts = {}

    for e in fetched:
        key = (e["principal_name"], e["principal_id"])
        counts[key] = counts.get(key, 0) + 1

    for (name, pid), count in sorted(counts.items(), key=lambda c: -c[1])[:5]:
        print(f"\t{count:5d}  {name}  {pid}")


def toDataframe(events, columns):
    return pd.DataFrame(events, columns=columns)
