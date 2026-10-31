#########################################################################################
# Filename    : __init__.py
# description : Web App Firewall section - registry of the available tools
#########################################################################################

from tools.waf import policies, protection_rules, recommendations

SECTION_NAME = "Web App Firewall"


def getTools():
    return [
        ("WAF policies in a compartment", policies.run),
        ("Protection rules in a WAF policy", protection_rules.run),
        ("Recommendations in a WAF policy", recommendations.run),
    ]
