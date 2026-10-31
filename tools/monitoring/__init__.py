#########################################################################################
# Filename    : __init__.py
# description : Metrics section - registry of the available tools
#########################################################################################

from tools.monitoring import metrics

SECTION_NAME = "Metrics"


def getTools():
    return [
        ("All metrics", metrics.run),
    ]
