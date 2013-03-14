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

import json
import logging

from django.utils.text import normalize_newlines
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.api import cinder
from openstack_dashboard.api import glance
from openstack_dashboard.api.eho import list_templates, create_cluster, create_node_template
from openstack_dashboard.usage import quotas

LOG = logging.getLogger(__name__)


class SelectProjectUserAction(workflows.Action):
    project_id = forms.ChoiceField(label=_("Project"))
    user_id = forms.ChoiceField(label=_("User"))

    def __init__(self, request, *args, **kwargs):
        super(SelectProjectUserAction, self).__init__(request, *args, **kwargs)
        projects = [(tenant.id, tenant.name)
                    for tenant in request.user.authorized_tenants]
        self.fields['project_id'].choices = projects

        users = [(request.user.id, request.user.username)]
        self.fields['user_id'].choices = users

    class Meta:
        name = _("Project & User")
        permissions = ("!",)


class SelectProjectUser(workflows.Step):
    action_class = SelectProjectUserAction
    contributes = ("project_id", "user_id")


class GeneralConfigurationAction(workflows.Action):

    def __init__(self, request, context, *args, **kwargs):
        super(GeneralConfigurationAction, self).__init__(request, context, *args, **kwargs)
        templates = list_templates(request)
        jt_nn_templates = ((t.name, t.name) for t in templates if ("jt" in t.name and "nn" in t.name))
        jt_templates = ((t.name, t.name) for t in templates if ("jt" in t.name and not "nn" in t.name))
        nn_templates = ((t.name, t.name) for t in templates if (not "jt" in t.name and "nn" in t.name))
        worker_templates = ((t.name, t.name) for t in templates if ("tt" in t.name and "dn" in t.name))

        self.fields['jt_nn_template_choices'].choices = jt_nn_templates
        self.fields['jt_template_choices'].choices = jt_templates
        self.fields['nn_template_choices'].choices = nn_templates
        self.fields['worker_template_choices'].choices = worker_templates

    name = forms.CharField(
        label=_("Cluster name"),
        required=True)

    base_image = forms.ChoiceField(
        label = _("Base image"),
        required = True)

    hadoop_cluster_topology = forms.ChoiceField(
        label = _("Hadoop cluster topology"),
        required = True,
        choices = [("Single-node mater", "Single-node mater"), ("Multi-node mater", "Multi-node mater")]
    )

    jt_nn_template_choices = forms.ChoiceField(
        required = False
    )

    jt_template_choices = forms.ChoiceField(
        required = False
    )

    nn_template_choices = forms.ChoiceField(
        required = False
    )

    worker_template_choices = forms.ChoiceField(
        required = False
    )

    result_field = forms.CharField(
        required = True
    )

    def populate_base_image_choices(self, request, context):
        public_images, _more = glance.image_list_detailed(request)
        return [(image.id, image.name) for image in public_images]


    class Meta:
        name = _("General configuration")
        help_text_template = ("project/hadoop/_cluster_general_help.html")

class GeneralConfiguration(workflows.Step):
    action_class = GeneralConfigurationAction
    contributes = ("name", "base_image", "templates")

    def contribute(self, data, context):
        context["name"] = data.get('name')
        context["base_image"] = data.get('base_image')
        context["templates"] = json.loads(data.get('result_field'))
        return context

class CreateCluster(workflows.Workflow):
    slug = "create_cluster"
    name = _("Create cluster")
    finalize_button_name = _("Create & Launch")
    success_url = "horizon:project:hadoop:index"
    default_steps = (GeneralConfiguration, )

    def handle(self, request, context):
        try:
            return create_cluster (
                request,
                context["name"],
                context["base_image"],
                context["templates"],
            )

        except:
            exceptions.handle(request)
            return False


class SetNameFlavorAction(workflows.Action):
    name = forms.CharField(
        label=_("Node Template Name"),
        required=True)

    flavor_id = forms.ChoiceField(
        label = _("Flavor"),
        required = True)

    class Meta:
        name = _("Template properties")
        help_text_template = ("project/hadoop/_template_general_help.html")

    def populate_flavor_id_choices(self, request, context):
        flavors = api.nova.flavor_list(request)
        flavor_list = [(flavor.name, flavor.name)
                       for flavor in flavors]
        return flavor_list

class SetNameFlavor(workflows.Step):
    action_class = SetNameFlavorAction
    contributes = ("name", "flavor_id")

class FillProcessPropertiesAction(workflows.Action):
    NODE_TYPE_CHOICES = (("JT+NN", "JT+NN"), ("NN", "NN"), ("JT", "JT"), ("TT+DN", "TT+DN"))

    node_type = forms.ChoiceField(
        label = _("Nodes type"),
        required = True,
        choices = NODE_TYPE_CHOICES)

    jt_heap_size = forms.CharField(
        label= mark_safe("Job tracker<br>heap size"),
        required=False)

    nn_heap_size = forms.CharField(
        label= mark_safe("Name node<br>heap size"),
        required=False)

    tt_heap_size = forms.CharField(
        label= mark_safe("Task tracker<br>heap size"),
        required=False)

    dn_heap_size = forms.CharField(
        label= mark_safe("Data node<br>heap size"),
        required=False)

    class Meta:
        name = _("Node types")
        help_text_template = ("project/hadoop/_process_properties_help.html")


class FillProcessProperties(workflows.Step):
    action_class =  FillProcessPropertiesAction
    contributes = ("node_type", "jt_heap_size", "nn_heap_size", "dn_heap_size", "tt_heap_size")


class CreateNodeTemplate(workflows.Workflow):
    slug = "create_node_template"
    name = _("Create Node Template")
    finalize_button_name =  _("Create")
    success_message = _("Created")
    failure_message = _("Could not create")
    success_url = "horizon:project:hadoop:index"
    default_steps = (SelectProjectUser, SetNameFlavor, FillProcessProperties)

    def handle(self, request, context):
        try:
            name = context["name"]
            node_type = context["node_type"]
            flavor_id = context["flavor_id"]
            jt_opts = {"heap_size": context["jt_heap_size"]}
            nn_opts = {"heap_size": context["nn_heap_size"]}
            tt_opts = {"heap_size": context["tt_heap_size"]}
            dn_opts = {"heap_size": context["dn_heap_size"]}
            return create_node_template(
                request,
                name,
                node_type,
                flavor_id,
                jt_opts,
                nn_opts,
                tt_opts,
                dn_opts)
        except:
            exceptions.handle(request)
            return False
