#########################################################################################
# Filename    : metrics.py
# description : Metrics - list the metrics of a compartment
#########################################################################################

import oci
import pandas as pd

from core.prompts import selectCompartment


def run(ctx):
    compartment = selectCompartment(ctx)

    metricsList = ctx.ocisdk.getMetricsList(
        compartmentID=compartment["id"],
        cfgName=ctx.profile,
    )

    return pd.DataFrame([oci.util.to_dict(metric) for metric in metricsList])
