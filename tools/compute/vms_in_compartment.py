#########################################################################################
# Filename    : vms_in_compartment.py
# description : Virtual Machines - list the VMs and volumes of a compartment
#########################################################################################

from core.prompts import selectCompartment
from tools.compute._common import vmDataframe, vmRows


def run(ctx):
    compartment = selectCompartment(ctx)

    return vmDataframe(vmRows(ctx, compartment["id"], compartment["name"]))
