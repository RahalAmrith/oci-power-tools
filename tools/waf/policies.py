#########################################################################################
# Filename    : policies.py
# description : Web App Firewall - list the WAF policies of a compartment
#########################################################################################

import pandas as pd

from core.prompts import selectCompartment


def run(ctx):
    compartment = selectCompartment(ctx)

    policyList = ctx.ocisdk.getFirewallPolicies(
        compartmentID=compartment["id"], cfgName=ctx.profile
    )

    return pd.DataFrame.from_dict(policyList)
