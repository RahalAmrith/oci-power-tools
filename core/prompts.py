#########################################################################################
# Filename    : prompts.py
# description : Interactive selection prompts shared by the tools
#########################################################################################


class ToolAbort(Exception):
    """Raised by a tool to stop cleanly, the message is shown to the user."""


def selectCompartment(ctx):
    print("\nFetching Compartment list")
    print("Please Wait. this may take some time\n")

    compartments = ctx.ocisdk.getCompartments(as_array=True, cfgName=ctx.profile)

    print("Select the relavant compartment number from the list\n")

    for i, c in enumerate(compartments):
        print(f"\t{i+1} - {c['name']}")

    cno = int(input("Enter compartment number : ")) - 1

    return compartments[cno]


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
