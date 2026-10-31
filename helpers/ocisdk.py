#########################################################################################
# Filename    : ocisdk.py
# Fi1eType    : Python Source file
# Author      : Rahal Amrith
# Created on  : 13/10/2022
# description : Python Class for OCI python SDK integration
#########################################################################################

import datetime
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta, timezone
import os

import oci
import json

from .utils import getProfilesFromConfig


# The audit log can only be paged one page of about 100 events at a time, so a busy
# compartment takes thousands of calls. The time window is cut into slices that are
# paged side by side. The audit API allows around 5 requests per second.
AUDIT_SLICE = timedelta(hours=6)
AUDIT_WORKERS = 5


class OCISDK:
    configs = {}

    def __init__(self, config_file_path=None):
        if config_file_path is None:
            CONFIG_FILE_PATH = os.getcwd() + "/configs/config.oci"
        else:
            CONFIG_FILE_PATH = config_file_path

        profiles = getProfilesFromConfig(CONFIG_FILE_PATH)

        for profile in profiles:
            cfg = oci.config.from_file(
                file_location=CONFIG_FILE_PATH, profile_name=profile
            )
            self.configs[profile] = cfg

    def getCompartments(self, as_array=False, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])

        compartmentList = oci.pagination.list_call_get_all_results(
            identity_client.list_compartments,
            compartment_id=self.configs[cfgName]["tenancy"],
            compartment_id_in_subtree=True,
        )

        compartments = {self.configs[cfgName]["tenancy"]: {"name": "root"}}

        if as_array:
            return [{"id": cmp.id, "name": cmp.name} for cmp in compartmentList.data]

        else:
            for cmp in compartmentList.data:
                compartments[cmp.id] = {"name": cmp.name}

            return compartments

    def getCompartmentActiveRegions(self, compartmentID=None, cfgName="DEFAULT"):
        """
        Goal: Get the list of active regions for a given compartment by checking
        the cost for the compartment in each region. If the cost is greater than 0,
        it means the compartment is active in that region.

        Without a compartment the whole tenancy is checked.
        """
        _now = datetime.datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        _start_time = _now - timedelta(days=31)
        _end_time = _now - timedelta(days=1)

        usage_client = oci.usage_api.UsageapiClient(self.configs[cfgName])

        usageFilter = None

        if compartmentID:
            usageFilter = oci.usage_api.models.Filter(
                operator="AND",
                dimensions=[
                    oci.usage_api.models.Dimension(
                        key="compartmentId", value=compartmentID
                    )
                ],
            )

        query = oci.usage_api.models.RequestSummarizedUsagesDetails(
            tenant_id=self.configs[cfgName]["tenancy"],
            time_usage_started=_start_time,
            time_usage_ended=_end_time,
            granularity="DAILY",
            is_aggregate_by_time=False,
            group_by=["region"],
            filter=usageFilter,
        )
        usage_resp = usage_client.request_summarized_usages(query)
        usage_resp = json.loads(str(usage_resp.data))

        activeRegions = set()

        for item in usage_resp["items"]:
            computed_amount = (
                float(item["computed_amount"])
                if item["computed_amount"] is not None
                else 0.0
            )
            if computed_amount > 0 and item["region"]:
                activeRegions.add(item["region"])

        return [{"region_name": region} for region in sorted(activeRegions)]

    def getUserGroups(self, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])

        groupsList = oci.pagination.list_call_get_all_results(
            identity_client.list_groups,
            compartment_id=self.configs[cfgName]["tenancy"],
        )

        groupsRes = []

        for cmp in groupsList.data:
            groupsRes.append(
                {
                    "defined_tags": cmp.defined_tags,
                    "description": cmp.description,
                    "freeform_tags": cmp.freeform_tags,
                    "id": cmp.id,
                    "inactive_status": cmp.inactive_status,
                    "lifecycle_state": cmp.lifecycle_state,
                    "name": cmp.name,
                    "time_created": cmp.time_created,
                }
            )

        return groupsRes

    def getUserDetails(self, userId, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])
        result = identity_client.get_user(user_id=userId)

        userDetail = {
            "description": result.data.description,
            "email": result.data.email,
            "email_verified": result.data.email_verified,
            "external_identifier": result.data.external_identifier,
            "id": result.data.id,
            "inactive_status": result.data.inactive_status,
            "is_mfa_activated": result.data.is_mfa_activated,
            "last_successful_login_time": result.data.last_successful_login_time,
            "name": result.data.name,
            "previous_successful_login_time": result.data.previous_successful_login_time,
            "time_created": str(result.data.time_created),
        }
        return userDetail

    def searchUser(self, query, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])

        all_users = oci.pagination.list_call_get_all_results(
            identity_client.list_users, compartment_id=self.configs[cfgName]["tenancy"]
        )

        all_users_data = json.loads(str(all_users.data))

        results = [
            user
            for user in all_users_data
            if query.lower() in str(user.get("name", "")).lower()
            or query.lower() in str(user.get("email", "")).lower()
            or query.lower() in str(user.get("id", "")).lower()
        ]
        return results

    def getGroupDetails(self, groupId, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])
        result = identity_client.get_group(group_id=groupId)

        groupDetail = {
            "defined_tags": result.data.defined_tags,
            "description": result.data.description,
            "freeform_tags": result.data.freeform_tags,
            "id": result.data.id,
            "inactive_status": result.data.inactive_status,
            "lifecycle_state": result.data.lifecycle_state,
            "name": result.data.name,
            "time_created": result.data.time_created,
        }
        return groupDetail

    def getGroupsforUser(self, userId, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])

        groupsList = oci.pagination.list_call_get_all_results(
            identity_client.list_user_group_memberships,
            compartment_id=self.configs[cfgName]["tenancy"],
            user_id=userId,
        )

        # userGroups = [grp.group_id for grp in groupsList]
        userGroups = []

        for grp in groupsList.data:
            userGroups.append(
                self.getGroupDetails(groupId=grp.group_id, cfgName=cfgName)
            )

        return userGroups

    def getUsersInGroup(self, groupId, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])

        result = oci.pagination.list_call_get_all_results(
            identity_client.list_user_group_memberships,
            compartment_id=self.configs[cfgName]["tenancy"],
            group_id=groupId,
        )

        userList = []

        for res in result.data:
            userList.append(self.getUserDetails(userId=res.user_id, cfgName=cfgName))

        return userList

    def getAllClustersInCompartment(self, compartmentID, cfgName="DEFAULT"):
        container_engine_client = oci.container_engine.ContainerEngineClient(
            self.configs[cfgName]
        )

        clusters = oci.pagination.list_call_get_all_results(
            container_engine_client.list_clusters, compartment_id=compartmentID
        )

        result = []

        for cluster in clusters.data:
            result.append(
                {
                    "name": cluster.name,
                    "id": cluster.id,
                    "kubernetes_version": cluster.kubernetes_version,
                }
            )

        return result

    def getAllPolicies(self, compartmentID, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])

        policiesList = oci.pagination.list_call_get_all_results(
            identity_client.list_policies, compartment_id=compartmentID
        )

        policyRes = []

        for pol in policiesList.data:
            policyRes.append(
                {
                    "id": pol.id,
                    "name": pol.name,
                    "statements": list(pol.statements),
                }
            )

        return policyRes

    def getAllVMs(self, compartmentID, cfgName="DEFAULT"):
        compute_engine_client = oci.core.ComputeClient(self.configs[cfgName])

        instanceList = oci.pagination.list_call_get_all_results(
            compute_engine_client.list_instances,
            compartment_id=compartmentID,
            limit=100,
        )

        # instanceList = compute_engine_client.list_instances(compartment_id=compartmentID)
        # print(len(instanceList.data))
        result = []

        for vm in instanceList.data:
            result.append(
                {
                    "name": vm.display_name,
                    "id": vm.id,
                    "state": vm.lifecycle_state,
                    "region": vm.region,
                    "shape": vm.shape,
                    "ocpu": vm.shape_config.ocpus,
                    "memory": vm.shape_config.memory_in_gbs,
                }
            )
        # print(result)
        return result

    def getAllVMsByTag(self, compartmentID, tagKey, tagValue, cfgName="DEFAULT"):
        tag_value_array = [v.strip() for v in tagValue.split(",")]

        compute_engine_client = oci.core.ComputeClient(self.configs[cfgName])

        instanceList = oci.pagination.list_call_get_all_results(
            compute_engine_client.list_instances,
            compartment_id=compartmentID,
            limit=100,
        )
        result = []

        freeform_tagged_instances = [
            i
            for i in instanceList.data
            if tagKey in i.freeform_tags and i.freeform_tags[tagKey] in tag_value_array
        ]
        defined_tagged_instances = [
            i
            for i in instanceList.data
            if tagKey in i.defined_tags and i.defined_tags[tagKey] in tag_value_array
        ]

        # Combine the filtered instances into a single list
        tagged_instances = freeform_tagged_instances + defined_tagged_instances

        for vm in tagged_instances:
            result.append(
                {
                    "name": vm.display_name,
                    "id": vm.id,
                    "state": vm.lifecycle_state,
                    "region": vm.region,
                    "shape": vm.shape,
                    "ocpu": vm.shape_config.ocpus,
                    "memory": vm.shape_config.memory_in_gbs,
                }
            )

        return result

    def getVolumesForVM(self, compartmentID, instanceID, cfgName="DEFAULT"):
        compute_engine_client = oci.core.ComputeClient(self.configs[cfgName])
        block_storage_client = oci.core.BlockstorageClient(self.configs[cfgName])

        volumeAttachmentList = oci.pagination.list_call_get_all_results(
            compute_engine_client.list_volume_attachments,
            compartment_id=compartmentID,
            instance_id=instanceID,
        )

        result = []

        for volAttachment in volumeAttachmentList.data:
            volDetails = block_storage_client.get_volume(volAttachment.volume_id)
            # print(volDetails.data)
            result.append(
                {
                    "name": volDetails.data.display_name,
                    "size_gb": volDetails.data.size_in_gbs,
                    "id": volDetails.data.id,
                    "state": volDetails.data.lifecycle_state,
                }
            )

        return result

    def getFirewallPolicies(self, compartmentID, cfgName="DEFAULT"):
        waas_client = oci.waas.WaasClient(self.configs[cfgName])

        policy_list = oci.pagination.list_call_get_all_results(
            waas_client.list_waas_policies, compartment_id=compartmentID
        )
        result = []

        for policy in policy_list.data:
            result.append(
                {
                    "display_name": policy.display_name,
                    "domain": policy.domain,
                    "id": policy.id,
                    "lifecycle_state": policy.lifecycle_state,
                    "time_created": policy.time_created,
                }
            )

        return result

    def getFirewallPolicyProtectionRules(self, policyID, cfgName="DEFAULT"):
        waas_client = oci.waas.WaasClient(self.configs[cfgName])

        # rules_list = waas_client.list_protection_rules(
        #     waas_policy_id=policyID, limit=100)

        rules_list = oci.pagination.list_call_get_all_results(
            waas_client.list_protection_rules, waas_policy_id=policyID, limit=100
        )

        result = []

        for rule in rules_list.data:
            result.append(
                {
                    "name": rule.name,
                    "action": rule.action,
                    "description": rule.description,
                    "key": rule.key,
                    "labels": " , ".join(map(str, rule.labels)),
                    "mod_security_rule_ids": " , ".join(
                        map(str, rule.mod_security_rule_ids)
                    ),
                }
            )

        return result

    def getFirewallPolicyRecommendations(self, policyID, cfgName="DEFAULT"):
        waas_client = oci.waas.WaasClient(self.configs[cfgName])

        rules_list = oci.pagination.list_call_get_all_results(
            waas_client.list_recommendations, waas_policy_id=policyID, limit=100
        )

        result = []

        for rule in rules_list.data:
            result.append(
                {
                    "key": rule.key,
                    "name": rule.name,
                    "mod_security_rule_ids": " , ".join(
                        map(str, rule.mod_security_rule_ids)
                    ),
                    "recommended_action": rule.recommended_action,
                    "description": rule.description,
                    "labels": " , ".join(map(str, rule.labels)),
                }
            )

        return result

    def getMetricsList(self, compartmentID, cfgName="DEFAULT"):
        monitoring_client = oci.monitoring.MonitoringClient(self.configs[cfgName])

        list_metrics_details = oci.monitoring.models.ListMetricsDetails(
            # name="EXAMPLE-name-Value",
            # namespace="EXAMPLE-namespace-Value",
            # resource_group="EXAMPLE-resourceGroup-Value",
            # dimension_filters={
            #     "EXAMPLE_KEY_ZDUw1": "EXAMPLE_VALUE_wpS4GaldHiPPjcgMqFCp"
            # },
            # group_by=["EXAMPLE--Value"],
            # sort_by="RESOURCEGROUP",
            # sort_order="DESC",
        )

        list_metrics_response = oci.pagination.list_call_get_all_results(
            monitoring_client.list_metrics,
            compartment_id=compartmentID,
            list_metrics_details=list_metrics_details,
            limit=100,
        )

        # result = []

        # for rule in list_metrics_response.data:
        #     result.append(
        #         {
        #             "key": rule.key,
        #             "name": rule.name,
        #             "mod_security_rule_ids": " , ".join(
        #                 map(str, rule.mod_security_rule_ids)
        #             ),
        #             "recommended_action": rule.recommended_action,
        #             "description": rule.description,
        #             "labels": " , ".join(map(str, rule.labels)),
        #         }
        #     )

        return list_metrics_response.data

    def getSubscribedRegions(self, cfgName="DEFAULT"):
        identity_client = oci.identity.IdentityClient(self.configs[cfgName])

        subscriptions = identity_client.list_region_subscriptions(
            self.configs[cfgName]["tenancy"]
        )

        return [sub.region_name for sub in subscriptions.data if sub.status == "READY"]

    def getAuditEvents(
        self,
        compartmentID,
        startTime,
        endTime,
        cfgName="DEFAULT",
        region=None,
        onPage=None,
    ):
        """onPage is called with the number of events of every page fetched, from
        several threads."""

        config = self.configs[cfgName]

        if region:
            config = dict(config, region=region)

        slices = []
        sliceStart = startTime

        while sliceStart < endTime:
            sliceEnd = min(sliceStart + AUDIT_SLICE, endTime)
            slices.append((sliceStart, sliceEnd))
            sliceStart = sliceEnd

        def fetchSlice(window):
            # A client per slice, so nothing is shared between the threads
            audit_client = oci.audit.AuditClient(config)

            events = []
            page = None

            while True:
                kwargs = {"retry_strategy": oci.retry.DEFAULT_RETRY_STRATEGY}

                if page:
                    kwargs["page"] = page

                response = audit_client.list_events(
                    compartment_id=compartmentID,
                    start_time=window[0],
                    end_time=window[1],
                    **kwargs,
                )
                events.extend(response.data)

                if onPage:
                    onPage(len(response.data))

                page = response.next_page

                if not page:
                    return events

        with ThreadPoolExecutor(max_workers=AUDIT_WORKERS) as pool:
            sliced = list(pool.map(fetchSlice, slices))

        result = []

        for event in (event for events in sliced for event in events):
            data = event.data
            identity = data.identity
            request = data.request
            response = data.response

            result.append(
                {
                    "time": event.event_time,
                    "event_name": data.event_name,
                    "source": event.source,
                    "action": getattr(request, "action", None),
                    "path": getattr(request, "path", None),
                    "status": getattr(response, "status", None),
                    "message": getattr(response, "message", None),
                    "resource_name": data.resource_name,
                    "resource_id": data.resource_id,
                    "compartment_id": data.compartment_id,
                    "compartment_name": data.compartment_name,
                    "principal_id": getattr(identity, "principal_id", None),
                    "principal_name": getattr(identity, "principal_name", None),
                    "auth_type": getattr(identity, "auth_type", None),
                    "ip_address": getattr(identity, "ip_address", None),
                    "user_agent": getattr(identity, "user_agent", None),
                }
            )

        return result
