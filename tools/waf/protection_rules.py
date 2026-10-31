#########################################################################################
# Filename    : protection_rules.py
# description : Web App Firewall - list the protection rules of a WAF policy
#########################################################################################

import pandas as pd

from tools.waf._common import selectWafPolicy


def run(ctx):
    selectedPolicy = selectWafPolicy(ctx)

    rulesList = ctx.ocisdk.getFirewallPolicyProtectionRules(
        policyID=selectedPolicy["id"], cfgName=ctx.profile
    )

    return pd.DataFrame.from_dict(rulesList)
