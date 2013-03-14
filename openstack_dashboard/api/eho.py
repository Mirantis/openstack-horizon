import json
import logging
import requests
from openstack_dashboard.api import glance, nova
from openstack_dashboard.api.base import url_for

try:
    from local.local_settings import EHO_ADDRESS
except ImportError:
    logging.warning("No local_settings file found.")


def get_eho_address(request):
    eho_address = 'endpoints'

    try:
        eho_address = EHO_ADDRESS
    except NameError:
        pass

    if eho_address == 'endpoints':
        return url_for(request, 'mapreduce')

    return eho_address + "/" + request.user.tenant_id


class NodeTemplate(object):
    def __init__(self, _id, node_template_name, node_type, flavor_name):
        self.id = _id
        self.name = node_template_name
        self.node_type = node_type
        self.flavor_name = flavor_name


class Cluster(object):
    def __init__(self, _id, name, node_templates, base_image, status,
                 nodes_count):
        self.id = _id
        self.name = name
        self.node_templates = node_templates
        self.base_image = base_image
        self.nodes_count = nodes_count
        self.status = status


class ClusterNode(object):
    def __init__(self, _id, vm, template_name, template_id):
        self.id = _id
        self.vm = vm
        self.template_name = template_name
        self.template_id = template_id


def list_clusters(request):
    token = request.user.token.id
    resp = requests.get(
        get_eho_address(request) + "/clusters",
        headers={"x-auth-token": token})
    if resp.status_code == 200:
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
            cluster = Cluster(id, name, _format_templates(node_templates),
                              base_image_name, status, len(nodes))
            clusters.append(cluster)
        return clusters
    else:
        return []


def _format_templates(tmpl_dict):
    formatted = []
    for tmpl in tmpl_dict.keys():
        formatted.append(tmpl + ": " + str(tmpl_dict[tmpl]))
    return formatted


def list_templates(request):
    token = request.user.token.id
    resp = requests.get(
        get_eho_address(request) + "/node-templates",
        headers={"x-auth-token": token,
                 "Content-Type": "application/json"})
    if resp.status_code == 200:
        templates_arr = resp.json["node_templates"]
        templates = []
        for template in templates_arr:
            id = template["id"]
            name = template["name"]
            flavor_id = template["flavor_id"]
            node_type = template["node_type"]["name"]
            templ = NodeTemplate(id, name, node_type, flavor_id)
            templates.append(templ)
        return templates
    else:
        return []


def create_cluster(request, name, base_image_id, templates):
    token = request.user.token.id
    post_data = {"cluster": {}}
    cluster_data = post_data["cluster"]
    cluster_data["base_image_id"] = base_image_id
    cluster_data["name"] = name
    cluster_data["node_templates"] = templates
    resp = requests.post(
        get_eho_address(request) + "/clusters",
        data=json.dumps(post_data),
        headers={"x-auth-token": token,
                 "Content-Type": "application/json"})

    return resp.status_code == 202


def create_node_template(request, name, node_type, flavor_id,
                         job_tracker_opts, name_node_opts, task_tracker_opts,
                         data_node_opts):
    token = request.user.token.id
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
    resp = requests.post(get_eho_address(request)
                         + "/node-templates",
                         json.dumps(post_data),
                         headers={
                             "x-auth-token": token,
                             "Content-Type": "application/json"
                         })

    return resp.status_code == 202


def terminate_cluster(request, cluster_id):
    token = request.user.token.id
    resp = requests.delete(
        get_eho_address(request) + "/clusters/" + cluster_id,
        headers={"x-auth-token": token})

    return resp.status_code == 204


def delete_template(request, template_id):
    token = request.user.token.id
    resp = requests.delete(
        get_eho_address(request) + "/node-templates/" + template_id,
        headers={"x-auth-token": token})

    return resp.status_code == 204


def get_cluster(request, cluster_id):
    token = request.user.token.id
    resp = requests.get(
        get_eho_address(request) + "/clusters/" + cluster_id,
        headers={"x-auth-token": token})
    cluster = resp.json["cluster"]

    return cluster


def get_node_template(request, node_template_id):
    token = request.user.token.id
    resp = requests.get(
        get_eho_address(request) + "/node-templates/" + node_template_id,
        headers={"x-auth-token": token})
    node_template = resp.json["node_template"]

    return node_template


def get_cluster_nodes(request, cluster_id):
    token = request.user.token.id
    resp = requests.get(
        get_eho_address(request) + "/clusters/" + cluster_id,
        headers={"x-auth-token": token})
    nodes = resp.json["cluster"]["nodes"]
    nodes_with_id = []
    for node in nodes:
        vm = nova.server_get(request, node["vm_id"])
        nodes_with_id.append(ClusterNode(vm.id, "%s (%s)" % (vm.name, ", ".join(
            [elem['addr'].__str__() for elem in vm.addresses['novanetwork']])),
                                         node["node_template"]["name"],
                                         node["node_template"]["id"]))

    return nodes_with_id
