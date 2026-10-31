#########################################################################################
# Filename    : all_vms.py
# description : Virtual Machines - list every VM and its volumes in the tenancy
#########################################################################################

from tools.compute._common import vmDataframe, vmRows


def run(ctx):
    print("\nFetching Virtual List")
    print("Please Wait. this may take some time\n")

    compartments = ctx.ocisdk.getCompartments(cfgName=ctx.profile)

    rows = []

    for cmp in compartments.keys():
        cmpName = compartments[cmp]["name"]

        print(f"\nScanning Compartment : {cmpName}")

        rows += vmRows(ctx, cmp, cmpName)

    return vmDataframe(rows)
