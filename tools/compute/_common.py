#########################################################################################
# Filename    : _common.py
# description : Logic shared by the virtual machine tools
#########################################################################################

import pandas as pd

VM_COLUMNS = [
    "compartment_name",
    "instance_name",
    "instance_state",
    "instance_region",
    "instance_shape",
    "instance_ocpu",
    "instance_memory",
    "volume_name",
    "volume_size_gb",
    "volume_state",
    "compartment_id",
    "instance_id",
    "volume_id",
]


def vmRows(ctx, compartmentId, compartmentName):
    """One row per attached volume of every VM in the compartment, VMs without volumes get one row of '--'."""

    rows = []

    for vm in ctx.ocisdk.getAllVMs(compartmentID=compartmentId, cfgName=ctx.profile):
        print(f"\tScanning instance : {vm['name']}")

        vols = ctx.ocisdk.getVolumesForVM(
            instanceID=vm["id"], compartmentID=compartmentId, cfgName=ctx.profile
        )

        for vol in vols or [None]:
            rows.append(
                {
                    "compartment_name": compartmentName,
                    "instance_name": vm["name"],
                    "instance_state": vm["state"],
                    "instance_region": vm["region"],
                    "instance_shape": vm["shape"],
                    "instance_ocpu": vm["ocpu"],
                    "instance_memory": vm["memory"],
                    "volume_name": vol["name"] if vol else "--",
                    "volume_size_gb": vol["size_gb"] if vol else "--",
                    "volume_state": vol["state"] if vol else "--",
                    "compartment_id": compartmentId,
                    "instance_id": vm["id"],
                    "volume_id": vol["id"] if vol else "--",
                }
            )

    return rows


def vmDataframe(rows):
    return pd.DataFrame(rows, columns=VM_COLUMNS)
