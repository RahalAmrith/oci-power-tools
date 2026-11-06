#########################################################################################
# Filename    : prompts.py
# description : Interactive selection prompts shared by the tools
#########################################################################################


import datetime

from tabulate import tabulate


TIME_WINDOWS = [
    ("Last 1 hour", datetime.timedelta(hours=1)),
    ("Last 24 hours", datetime.timedelta(days=1)),
    ("Last 7 days", datetime.timedelta(days=7)),
    ("Last 30 days", datetime.timedelta(days=30)),
]
MAX_WINDOW_DAYS = 365
MAX_COMPARTMENT_ROWS = 20


class ToolAbort(Exception):
    """Raised by a tool to stop cleanly, the message is shown to the user."""


def printCompartmentTable(compartments):
    """Fills each column top to bottom, MAX_COMPARTMENT_ROWS entries per column."""

    rowCount = min(len(compartments), MAX_COMPARTMENT_ROWS)
    columnCount = -(-len(compartments) // MAX_COMPARTMENT_ROWS)
    numWidth = max(2, len(str(len(compartments))))
    rows = []

    for r in range(rowCount):
        row = []

        for c in range(columnCount):
            i = c * MAX_COMPARTMENT_ROWS + r
            row.append(
                f"{i + 1:0{numWidth}d} - {compartments[i]['name']}"
                if i < len(compartments)
                else ""
            )

        rows.append(row)

    print("")
    print(tabulate(rows, tablefmt="rounded_outline", disable_numparse=True))


def selectCompartment(ctx, includeRoot=False):
    print("\nFetching Compartment list")
    print("Please Wait. this may take some time\n")

    compartments = ctx.ocisdk.getCompartments(as_array=True, cfgName=ctx.profile)

    if includeRoot:
        root = {"id": ctx.ocisdk.configs[ctx.profile]["tenancy"], "name": "root"}
        compartments = [root] + compartments

    if not compartments:
        raise ToolAbort("ERROR : No compartments found.")

    print("Select the relavant compartment number from the list")
    printCompartmentTable(compartments)

    while True:
        choice = str(input("\nEnter compartment number (q = cancel) : ")).strip().lower()

        if choice == "q":
            raise ToolAbort("Cancelled.")

        if choice.isdigit() and 1 <= int(choice) <= len(compartments):
            return compartments[int(choice) - 1]

        print("Error : Invalid option")


def selectUser(ctx):
    query = str(input("\nEnter the User's Name or email or ocid: "))

    users = ctx.ocisdk.searchUser(query=query, cfgName=ctx.profile)

    if not users:
        raise ToolAbort("ERROR : User not found.")

    print("Select the user from the list below : \n")

    for i, user in enumerate(users):
        print(f"{i+1}. {user['name']} ({user['email']})")
    print("\n")

    choice = int(input("\nEnter your choice : ")) - 1

    if not 0 <= choice < len(users):
        raise ToolAbort("Invalid choice.")

    return users[choice]


def selectTimeWindow():
    """Returns (start, end) as timezone aware UTC datetimes."""

    print("\nSelect the time window :\n")

    for i, (label, _) in enumerate(TIME_WINDOWS):
        print(f"\t{i+1} : {label}")

    customOpt = len(TIME_WINDOWS) + 1
    print(f"\t{customOpt} : Custom number of days")

    choice = str(input("\nEnter option number : ")).strip()

    if choice.isdigit() and 1 <= int(choice) <= len(TIME_WINDOWS):
        span = TIME_WINDOWS[int(choice) - 1][1]

    elif choice == str(customOpt):
        days = str(input(f"Enter the number of days (1 - {MAX_WINDOW_DAYS}) : "))
        days = days.strip()

        if not days.isdigit() or not 1 <= int(days) <= MAX_WINDOW_DAYS:
            raise ToolAbort("Invalid number of days.")

        span = datetime.timedelta(days=int(days))

    else:
        raise ToolAbort("Invalid choice.")

    end = datetime.datetime.now(datetime.timezone.utc)

    return end - span, end


def askIncludeReads():
    """Audit logs are mostly read calls, so they are hidden unless asked for."""

    answer = str(input("\nInclude read events (GET / HEAD)? [y/N] : ")).strip().lower()

    return answer in ("y", "yes")
