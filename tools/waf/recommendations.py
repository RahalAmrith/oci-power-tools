#########################################################################################
# Filename    : recommendations.py
# description : Web App Firewall - list the recommendations of a WAF policy
#########################################################################################

import pandas as pd

from tools.waf._common import selectWafPolicy


def run(ctx):
    selectedPolicy = selectWafPolicy(ctx)

    rulesList = ctx.ocisdk.getFirewallPolicyRecommendations(
        policyID=selectedPolicy["id"], cfgName=ctx.profile
    )

    return pd.DataFrame.from_dict(rulesList)
