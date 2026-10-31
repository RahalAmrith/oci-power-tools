#########################################################################################
# Filename    : _common.py
# description : Logic shared by the web application firewall tools
#########################################################################################

from core.prompts import selectCompartment


def selectWafPolicy(ctx):
    compartment = selectCompartment(ctx)

    policyList = ctx.ocisdk.getFirewallPolicies(
        compartmentID=compartment["id"], cfgName=ctx.profile
    )

    print("\nWAF Policy List : ")
    for i, policy in enumerate(policyList):
        print(f"\t{i+1} - {policy['display_name']} - {policy['domain']}")

    userInput = int(input("\nEnter the policy number : ")) - 1

    return policyList[userInput]
