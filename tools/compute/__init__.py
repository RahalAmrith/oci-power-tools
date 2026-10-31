#########################################################################################
# Filename    : __init__.py
# description : Virtual Machines section - registry of the available tools
#########################################################################################

from tools.compute import all_vms, vms_by_tag, vms_in_compartment

SECTION_NAME = "Virtual Machines"


def getTools():
    return [
        ("All VMs in tenancy", all_vms.run),
        ("VMs in a compartment", vms_in_compartment.run),
        ("VMs by tag", vms_by_tag.run),
    ]
