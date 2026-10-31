#########################################################################################
# Filename    : __init__.py
# description : Container Engine section - registry of the available tools
#########################################################################################

from tools.container_engine import clusters

SECTION_NAME = "Container Engine"


def getTools():
    return [
        ("All clusters", clusters.run),
    ]
