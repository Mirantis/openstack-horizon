import json
import requests
from clusters import Cluster
from openstack_dashboard import api
from openstack_dashboard.api import glance, nova
from templates import Template

EHO_IP = "http://127.0.0.1:8080/v0.2"

def list_clusters(tenant_id, request, token):
    resp = requests.get(EHO_IP + "/" + tenant_id + "/clusters", headers={"x-auth-token": token})
    if (resp.status_code == 200):
        clusters_arr = resp.json["clusters"]
        clusters = []
        for cl in clusters_arr:
            id = cl["id"]
            name = cl["name"]
            base_image_id = cl["base_image_id"]
            base_image_name = glance.image_get(request, base_image_id).name
            node_templates = cl["node_templates"]
            status = cl["status"]
            nodes = cl["nodes"]
            cluster = Cluster(id, name, format_templates(node_templates), base_image_name, status, len(nodes))
            clusters.append(cluster)
        return clusters

    else:
        return []

def format_templates(templ_dict):
    formatted = []
    for tmpl in templ_dict.keys():
        formatted.append(tmpl + ": " + str(templ_dict[tmpl]))
    return formatted


def list_templates(tenant_id, token):
    resp = requests.get(EHO_IP + "/" + tenant_id + "/node-templates", headers={"x-auth-token": token, "Content-Type" : "application/json"})
    if (resp.status_code == 200):
        templates_arr = resp.json["node_templates"]
        templates = []
        for template in templates_arr:
            id = template["id"]
            name = template["name"]
            flavor_id = template["flavor_id"]
            node_type = template["node_type"]["name"]
            templ = Template(id, name, node_type, flavor_id)
            templates.append(templ)
        return templates
    else:
        return []

def create_cluster(base_image_id, name, tenant_id, templates, token):
    post_data = {"cluster": {}}
    cluster_data = post_data["cluster"]
    cluster_data["base_image_id"] = base_image_id
    cluster_data["name"] = name
    cluster_data["node_templates"] = templates
    resp = requests.post(EHO_IP + "/" + tenant_id + "/clusters.json", data=json.dumps(post_data), headers={"x-auth-token": token, "Content-Type" : "application/json"})
    return resp.status_code == 202

def create_node_template(name, tenant_id, node_type, flavor_id, job_tracker_opts, name_node_opts, task_tracker_opts, data_node_opts, token):
    post_data = {"node_template": {}}
    template_data = post_data["node_template"]
    template_data["name"] = name
    template_data["node_type"] = node_type
    template_data["flavor_id"] = flavor_id
    if "jt" in str(node_type).lower():
        template_data["job_tracker"] = job_tracker_opts
    if "nn" in str(node_type).lower():
        template_data["name_node"] = name_node_opts
    if "tt" in str(node_type).lower():
        template_data["task_tracker"] = task_tracker_opts
    if "dn" in str(node_type).lower():
        template_data["data_node"] = data_node_opts
    resp = requests.post(EHO_IP + "/" + tenant_id + "/node-templates.json", json.dumps(post_data), headers={"x-auth-token": token, "Content-Type" : "application/json"})

    return resp.status_code == 202


def terminate_cluster(cluster_id, tenant_id, token):
    resp = requests.delete(EHO_IP + "/" + tenant_id + "/clusters/" + cluster_id, headers={"x-auth-token": token})
    return resp.status_code == 204

def delete_template(template_id, tenant_id, token):
    resp = requests.delete(EHO_IP + "/" + tenant_id + "/node-templates/" + template_id, headers={"x-auth-token": token})
    return resp.status_code == 204

def get_cluster(cluster_id, tenant_id, token):
    resp = requests.get(EHO_IP + "/" + tenant_id + "/clusters/" + cluster_id, headers={"x-auth-token": token})
    cluster = resp.json["cluster"]
    return cluster

def get_node_template(node_template_id, tenant_id, token):
    resp = requests.get(EHO_IP + "/" + tenant_id + "/node-templates/" + node_template_id, headers={"x-auth-token": token})
    node_template = resp.json["node_template"]
    return node_template

class ClusterNode:
    def __init__(self, id, vm, template_name, template_id):
        self.id = id
        self.vm = vm
        self.template_name = template_name
        self.template_id = template_id


def get_cluster_nodes(cluster_id, tenant_id, request, token):
    resp = requests.get(EHO_IP + "/" + tenant_id + "/clusters/" + cluster_id, headers={"x-auth-token": token})
    nodes = resp.json["cluster"]["nodes"]
    nodes_with_id = []
    for node in nodes:
        vm = api.nova.server_get(request, node["vm_id"])
        nodes_with_id.append(ClusterNode(vm.id, "%s (%s)" % (vm.name, ", ".join([elem['addr'].__str__() for elem in vm.addresses['novanetwork']])), node["node_template"]["name"], node["node_template"]["id"]))
    return nodes_with_id



