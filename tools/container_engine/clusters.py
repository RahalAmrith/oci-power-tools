#########################################################################################
# Filename    : clusters.py
# description : Container Engine - list the clusters of every compartment
#########################################################################################

import pandas as pd


def run(ctx):
    print("\nFetching Clusters List list")
    print("Please Wait. this may take some time\n")

    compartments = ctx.ocisdk.getCompartments(cfgName=ctx.profile)

    rows = []

    for cmp in compartments.keys():
        clustersList = ctx.ocisdk.getAllClustersInCompartment(
            compartmentID=cmp, cfgName=ctx.profile
        )

        for cluster in clustersList:
            rows.append(
                {
                    "compartment": compartments[cmp]["name"],
                    "name": cluster["name"],
                    "id": cluster["id"],
                    "kubernetes_version": cluster["kubernetes_version"],
                }
            )

    return pd.DataFrame(
        rows, columns=["compartment", "name", "id", "kubernetes_version"]
    )
