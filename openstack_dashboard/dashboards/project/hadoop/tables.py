# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django import shortcuts
from django import template
from django.core import urlresolvers
from django.template.defaultfilters import title
from django.utils.http import urlencode
from django.utils.translation import string_concat, ugettext_lazy as _

from horizon import tables
from openstack_dashboard.api.eho import delete_template, terminate_cluster


LOG = logging.getLogger(__name__)

class CreateNodeTemplate(tables.LinkAction):
    name = "create_node_template"
    verbose_name = _("Create Template")
    url = "horizon:project:hadoop:create_template"
    classes = ("btn-create", "ajax-modal")

    def allowed(self, request, datum):
        return True



class EditTemplate(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Template")
    url = "horizon:project:hadoop:edit_template"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, template):
        return True


class DeleteTemplate(tables.BatchAction):
    name = "delete_template"
    verbose_name = _("Delete Template")
    classes = ("btn-terminate", "btn-danger")

    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Template")
    data_type_plural = _("Templates")

    def allowed(self, request, template):
        return True

    def action(self, request, template_id):
        delete_template(request, template_id)


class CreateCluster(tables.LinkAction):
    name = "create_cluster"
    verbose_name = _("Create Cluster")
    url = "horizon:project:hadoop:create_cluster"

    classes = ("ajax-modal", "btn-launch")
    action_present = _("Create")
    action_past = _("Created")

    data_type_singular = _("Cluster")
    data_type_plural = _("Cluster")

    def allowed(self, request, datum):
        return True

class EditCluster(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Cluster")
    url = "horizon:project:hadoop:edit_cluster"
    classes = ("ajax-modal", "btn-edit")

    def allowed(self, request, cluster):
        return True

class TerminateCluster(tables.BatchAction):
    name = "terminate"
    verbose_name = _("Terminate Cluster")

    classes = ("btn-terminate", "btn-danger")

    action_present = _("Terminate")
    action_past = _("Terminated")
    data_type_singular = _("Cluster")
    data_type_plural = _("Clusters")

    def allowed(self, request, template):
        return True

    def action(self, request, cluster_id):
        terminate_cluster(request, cluster_id)


def render_templates(instance):
    template_name = 'project/hadoop/_nodes_list.html'
    context = {"cluster": instance}
    return template.loader.render_to_string(template_name, context)

class ClustersTable(tables.DataTable):
    STATUS_CHOICES = (
        ("Active", True),
        ("Starting", None),
        ("Stopping", None)
    )

    name = tables.Column("name",
        link=("horizon:project:hadoop:cluster_details"),
        verbose_name=_("Cluster Name"))

    node_template = tables.Column(render_templates,
        verbose_name=_("Node Templates"))

    base_image = tables.Column("base_image",
        verbose_name=_("Base Image"))

    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=False,
                           status_choices=STATUS_CHOICES)

    nodes_count = tables.Column("nodes_count",
        verbose_name=_("Nodes Count"))

    class Meta:
        name = "clusters"
        verbose_name = _("Hadoop Clusters")
        status_columns = ["status"]
        table_actions = (CreateCluster, TerminateCluster)
        row_actions = EditCluster, TerminateCluster



class NodeTemplatesTable(tables.DataTable):
    name = tables.Column("name",
        verbose_name=_("Node template name"),
        link=("horizon:project:hadoop:node_template_details"))
    node_type = tables.Column("node_type", verbose_name=_("Node Type"))
    flavor_name = tables.Column("flavor_name", verbose_name=_("Flavor name"))

    class Meta:
        name = "node_templates"
        verbose_name = _("Node Templates")
        table_actions = (CreateNodeTemplate, DeleteTemplate)
        row_actions = (EditTemplate, DeleteTemplate)


