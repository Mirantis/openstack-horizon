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
from openstack_dashboard.usage import quotas

from .templates import addImage
from  ehoclient import list_templates, create_cluster, create_node_template

LOG = logging.getLogger(__name__)


class SelectProjectUserAction(workflows.Action):
    project_id = forms.ChoiceField(label=_("Project"))
    user_id = forms.ChoiceField(label=_("User"))

    def __init__(self, request, *args, **kwargs):
        super(SelectProjectUserAction, self).__init__(request, *args, **kwargs)
        # Set our project choices
        projects = [(tenant.id, tenant.name)
                    for tenant in request.user.authorized_tenants]
        self.fields['project_id'].choices = projects

        # Set our user options
        users = [(request.user.id, request.user.username)]
        self.fields['user_id'].choices = users

    class Meta:
        name = _("Project & User")
        # Unusable permission so this is always hidden. However, we
        # keep this step in the workflow for validation/verification purposes.
        permissions = ("!",)


class SelectProjectUser(workflows.Step):
    action_class = SelectProjectUserAction
    contributes = ("project_id", "user_id")


class NameAction(workflows.Action):
    name = forms.CharField(widget=forms.Textarea,
        label=_("Cluster name"),
        required=True,
        help_text=_("This name would be used further"))
    base_image = forms.ChoiceField(label = _("Base image"),
        required = True)
    class Meta:
        name = _("Cluster name")
        help_text_template = ("project/hadoop/_cluster_general_help.html")

    def populate_base_image_choices(self, request, context):
        images = []
        images.append(("m1.small", "m1.small"))
        images.append(("m1.medium", "m1.medium"))
        images.append(("m1.large", "m1.large"))
        images.append(("m1.xlarge", "m1.xlarge"))
        return images

class NameStep(workflows.Step):
    action_class = NameAction
    contributes = ("name", "base_image")

class NodesAction(workflows.Action):
    primary_node_template = forms.ChoiceField(
        label = mark_safe("<h3>Primary node template</h3><br/><h4>Node Template name</h4>"),
        required = True
    )

    secondary_node_template = forms.ChoiceField(
        label = mark_safe("<h3>Secondary node template</h3><br/><h4>Node Template name</h4>"),
        required = True
    )

    secondary_node_template_count = forms.IntegerField(
        widget=forms.Textarea,
        label =  _("count"),
        initial = 1,
        required = True)

    def populate_primary_node_template_choices(self, request, context):
        templates = list_templates()
        primary_templates = ((t.name, t.name) for t in templates if ("jt" in t.name or "nn" in t.name))
        return primary_templates

    def populate_secondary_node_template_choices(self, request, context):
        templates = list_templates()
        secondary_templates = ((t.name, t.name) for t in templates if ("tt" in t.name or "dn" in t.name))
        return secondary_templates

    class Meta:
        name = _("Template images")
        help_text_template = ("project/hadoop/_cluster_templates_help.html")



class NodesStep(workflows.Step):
    action_class = NodesAction
    contributes = ("primary_node_template", "secondary_node_template", "secondary_node_template_count")


class CreateCluster(workflows.Workflow):
    slug = "create_cluster"
    name = _("Create cluster")
    finalize_button_name = _("Create & Launch")
    success_url = "horizon:project:hadoop:index"
    default_steps = (NameStep, NodesStep)

    def handle(self, request, context):
        try:
            return create_cluster(
                context["base_image"],
                context["name"],
                context["primary_node_template"],
                context["secondary_node_template"],
                context["secondary_node_template_count"]
            )
        except:
            exceptions.handle(request)
            return False



class FillPropertiesAction(workflows.Action):
    name = forms.CharField(widget=forms.Textarea,
        label=_("Node Template Name"),
        required=True,
        help_text=_("This name should be unique"))

    flavor_id = forms.ChoiceField(label = _("Flavor"),
        required = True)

    class Meta:
        name = _("Template properties")
        help_text_template = ("project/hadoop/_template_general_help.html")

    def populate_flavor_id_choices(self, request, context):
        flavors_list = [("id_small", "m1.small"), ("id_medium", "m1.medium"), ("id_large", "m1.large"), ("id_xlarge", "m1.xlarge")]
        return flavors_list

class FillProperties(workflows.Step):
    contributes = ("name", "flavor_id")
    action_class = FillPropertiesAction




class FillProcessPropertiesAction(workflows.Action):
    NODE_TYPE_CHOICES = (("JT+NN", "JT+NN"), ("NN", "NN"), ("JT", "JT"), ("TT+DN", "TT+DN"))
    node_type = forms.ChoiceField(label = _("Nodes type"), required = True, choices = NODE_TYPE_CHOICES)


    jt_heap_size = forms.CharField(widget=forms.Textarea,
        label= mark_safe("Job tracker<br>heap size"),
        required=False)

    nn_heap_size = forms.CharField(widget=forms.Textarea,
        label= mark_safe("Name node<br>heap size"),
        required=False)

    tt_heap_size = forms.CharField(widget=forms.Textarea,
        label= mark_safe("Task tracker<br>heap size"),
        required=False)

    dn_heap_size = forms.CharField(widget=forms.Textarea,
        label= mark_safe("Data node<br>heap size"),
        required=False)


    class Meta:
        name = _("Node types")
        help_text_template = ("project/hadoop/_process_properties_help.html")



class FillProcessProperties(workflows.Step):
    contributes = ("node_type", "jt_heap_size", "nn_heap_size", "dn_heap_size", "tt_heap_size")
    action_class =  FillProcessPropertiesAction



class CreateNodeTemplate(workflows.Workflow):
    slug = "create_node_template"
    name = _("Create Node Template")
    finalize_button_name =  _("Create")
    success_message = _("Created")
    failure_message = _("Could not create")
    success_url = "horizon:project:hadoop:index"
    default_steps = (SelectProjectUser, FillProperties, FillProcessProperties)

    def format_status_message(self, message):
        return message

    def handle(self, request, context):
        name = context["name"]
        node_type = context["node_type"]
        flavor_id = context["flavor_id"]
        jt_opts = {"heap_size": context["jt_heap_size"]}
        nn_opts = {"heap_size": context["nn_heap_size"]}
        tt_opts = {"heap_size": context["tt_heap_size"]}
        dn_opts = {"heap_size": context["dn_heap_size"]}
        return create_node_template(name, node_type, flavor_id, jt_opts, nn_opts, tt_opts, dn_opts)
