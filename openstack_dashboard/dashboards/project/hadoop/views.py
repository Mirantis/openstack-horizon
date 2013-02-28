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
from .tables import InstancesTable
from .tables import NodeTemplatesTable
from .workflows import CreateCluster, CreateNodeTemplate
from .clusters import Cluster
from .templates import Template, getImages, addImage
from .tabs import ClusterDetailTabs, NodeTemplateDetailsTabs
from .clusters import getClusters, find_cluster

from ehoclient import list_clusters, list_templates


LOG = logging.getLogger(__name__)


class IndexView(tables.MultiTableView):
    table_classes = InstancesTable, NodeTemplatesTable
    template_name = 'project/hadoop/index.html'

    def get_node_templates_data(self):
        # Gather our node_templates
        try:
            #node_templates = api.nova.server_list(self.request)
            #image1 = Image(0, "jt_nn.xlarge", "JT+NN", "m1.xlarge" )
            node_templates = list_templates()

            #get from client
        except:
            node_templates = []
            exceptions.handle(self.request,
                              _('Unable to retrieve node_templates.'))
        # Gather our flavors and correlate our node_templates to them

        return node_templates

    def get_clusters_data(self):
        # Gather our clusters
        try:
            #clusters = api.nova.server_list(self.request)
            #c11 = Cluster(123, "Cluster1", "JT+NN, TT, DN", "m1.xlarge", "active", 10)
            #c12 = Cluster(456, "Cluster2", "JT, NN", "m1.xlarge", "shutoff", 15)
            #clusters = [c11, c12]
            clusters = list_clusters(self.request)
            #get from client
        except:
            clusters = []
            exceptions.handle(self.request,
                _('Unable to retrieve clusters.'))
            # Gather our flavors and correlate our clusters to them

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
#        if not hasattr(self, "_object"):
#            instance_id = self.kwargs['instance_id']
#            try:
#                self._object = api.nova.server_get(self.request, instance_id)
#            except:
#                redirect = reverse("horizon:project:instances:index")
#                msg = _('Unable to retrieve instance details.')
#                exceptions.handle(self.request, msg, redirect=redirect)
#        return self._object

    def get_initial(self):
        pass
#        return {'instance': self.kwargs['instance_id'],
#                'tenant_id': self.request.user.tenant_id,
#                'name': getattr(self.get_object(), 'name', '')}

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