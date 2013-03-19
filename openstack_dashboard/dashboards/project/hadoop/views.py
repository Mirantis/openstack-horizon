# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

"""
Views for managing instances.
"""
import logging

from django import http
from django import shortcuts
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon import tables
from horizon import workflows

from openstack_dashboard import api
from .forms import UpdateInstance, UpdateTemplate
from openstack_dashboard.api.eho import list_templates, list_clusters
from .tables import NodeTemplatesTable, ClustersTable
from .workflows import CreateCluster, CreateNodeTemplate
from .tabs import ClusterDetailTabs, NodeTemplateDetailsTabs



LOG = logging.getLogger(__name__)


class IndexView(tables.MultiTableView):
    table_classes = ClustersTable, NodeTemplatesTable
    template_name = 'project/hadoop/index.html'

    def get_node_templates_data(self):
        try:
            node_templates = list_templates(self.request)
        except:
            node_templates = []
            exceptions.handle(self.request,
                              _('Unable to retrieve node_templates.'))
        return node_templates

    def get_clusters_data(self):
        try:
            clusters = list_clusters(self.request)
        except:
            clusters = []
            exceptions.handle(self.request,
                _('Unable to retrieve clusters.'))

        return clusters


class EditClusterView(forms.ModalFormView):
    form_class = UpdateInstance
    template_name = 'project/hadoop/update.html'
    context_object_name = 'cluster'
    success_url = reverse_lazy("horizon:project:hadoop:index")

    def get_context_data(self, **kwargs):
        context = super(EditClusterView, self).get_context_data(**kwargs)
        context["instance_id"] = self.kwargs['instance_id']
        return context

    def get_object(self, *args, **kwargs):
        pass

    def get_initial(self):
        pass
#

class EditTemplateView(forms.ModalFormView):
    form_class = UpdateTemplate
    context_object_name = "template"
    template_name = 'project/hadoop/update_template.html'
    success_url = reverse_lazy("horizon:project:hadoop:index")

    def get_context_data(self, **kwargs):
        context = super(EditTemplateView, self).get_context_data(**kwargs)
        context["template_id"] = self.kwargs['template_id']
        return context

    def get_object(self, *args, **kwargs):
        pass

    def get_initial(self):
        pass


class CreateClusterView(workflows.WorkflowView):
    workflow_class = CreateCluster
    template_name = "project/hadoop/launch.html"

    def get_initial(self):
        initial = super(CreateClusterView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial


class CreateClusterView(workflows.WorkflowView):
    workflow_class = CreateCluster
    template_name = "project/hadoop/create_cluster.html"

    def get_initial(self):
        initial = super(CreateClusterView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial


class CreateNodeTemplateView(workflows.WorkflowView):
    workflow_class = CreateNodeTemplate
    template_name = "project/hadoop/create_node_template.html"

    def get_initial(self):
        initial = super(CreateNodeTemplateView, self).get_initial()
        initial['project_id'] = self.request.user.tenant_id
        initial['user_id'] = self.request.user.id
        return initial


class ClusterDetailView(tabs.TabView):
    tab_group_class = ClusterDetailTabs
    template_name = 'project/hadoop/cluster_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ClusterDetailView, self).get_context_data(**kwargs)
        return context

    def get_data(self):
        pass


class NodeTemplateDetailView(tabs.TabView):
    tab_group_class = NodeTemplateDetailsTabs
    template_name = 'project/hadoop/node_template_details.html'

    def get_context_data(self, **kwargs):
        context = super(NodeTemplateDetailView, self).get_context_data(**kwargs)
        return context