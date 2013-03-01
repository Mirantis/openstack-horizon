import json
import requests
from clusters import Cluster
from openstack_dashboard import api
from openstack_dashboard.api import glance, nova
from templates import Template

EHO_IP = "http://127.0.0.1:8080/v0.1"

def list_clusters(request):
    resp = requests.get(EHO_IP + "/clusters")
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


def list_templates():
    resp = requests.get(EHO_IP + "/node-templates")
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


def create_cluster(base_image_id, name, primary_node_template, secondary_node_template, secondary_node_template_count):
    post_data = {}
    post_data["base_image_id"] = base_image_id
    post_data["name"] = name
    post_data["tenant_id"] = "tenant-1"
    post_data["node_templates"] = {primary_node_template: 1, secondary_node_template: secondary_node_template_count}
    resp = requests.post(EHO_IP + "/clusters", data=json.dumps(post_data))
    return resp.status_code == 202

def create_cluster_NEW(base_image_id, name, templates):
    post_data = {}
    post_data["base_image_id"] = base_image_id
    post_data["name"] = name
    post_data["tenant_id"] = "tenant-1"
    post_data["node_templates"] = templates
    resp = requests.post(EHO_IP + "/clusters", data=json.dumps(post_data))
    return resp.status_code == 202

def create_node_template(name, node_type, flavor_id, job_tracker_opts, name_node_opts, task_tracker_opts, data_node_opts):
    post_data = {}
    post_data["name"] = name
    post_data["node_type"] = node_type
    post_data["flavor_id"] = flavor_id
    post_data["tenant_id"] = "tenant-1"
    if "jt" in str(node_type).lower():
        post_data["job_tracker"] = job_tracker_opts
    if "nn" in str(node_type).lower():
        post_data["name_node"] = name_node_opts
    if "tt" in str(node_type).lower():
        post_data["task_tracker"] = task_tracker_opts
    if "dn" in str(node_type).lower():
        post_data["data_node"] = data_node_opts
    resp = requests.post(EHO_IP + "/node-templates", json.dumps(post_data))

    return resp.status_code == 202


def terminate_cluster(cluster_id):
    resp = requests.delete(EHO_IP + "/clusters/" + cluster_id)
    return resp.status_code == 204

def delete_template(template_id):
    resp = requests.delete(EHO_IP + "/node-templates/" + template_id)
    return resp.status_code == 204

def get_cluster(cluster_id):
    resp = requests.get(EHO_IP + "/clusters/" + cluster_id)
    cluster = resp.json
    return cluster

def get_node_template(node_template_id):
    resp = requests.get(EHO_IP + "/node-templates/" + node_template_id)
    node_template = resp.json
    return node_template

class ClusterNode:
    def __init__(self, id, vm, template_name, template_id):
        self.id = id
        self.vm = vm
        self.template_name = template_name
        self.template_id = template_id


def get_cluster_nodes(cluster_id, request):
    resp = requests.get(EHO_IP + "/clusters/" + cluster_id)
    nodes = resp.json["nodes"]
    nodes_with_id = []
    for node in nodes:
        vm = api.nova.server_get(request, node["vm_id"])
        nodes_with_id.append(ClusterNode(vm.id, "%s (%s)" % (vm.name, ", ".join([elem['addr'].__str__() for elem in vm.addresses['supernetwork']])), node["node_template"]["name"], node["node_template"]["id"]))
    return nodes_with_id



