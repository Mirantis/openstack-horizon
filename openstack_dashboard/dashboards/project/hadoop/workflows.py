# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging

from django.utils.text import normalize_newlines
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.api import glance
from openstack_dashboard.api.eho import list_templates, create_cluster, \
    create_node_template

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
        super(GeneralConfigurationAction, self).__init__(request, context,
            *args, **kwargs)
        templates = list_templates(request)
        jt_nn_templates = ((t.name, t.name) for t in templates
            if ("JT+NN" == t.node_type))
        jt_templates = ((t.name, t.name) for t in templates
            if ("JT" == t.node_type))
        nn_templates = ((t.name, t.name) for t in templates
            if ("NN" == t.node_type))
        worker_templates = ((t.name, t.name) for t in templates
            if ("TT+DN" == t.node_type))

        self.fields['jt_nn_template_choices'].choices = jt_nn_templates
        self.fields['jt_template_choices'].choices = jt_templates
        self.fields['nn_template_choices'].choices = nn_templates
        self.fields['worker_template_choices'].choices = worker_templates

        self.templates = templates
        self.template_infos = {}
        flavors = api.nova.flavor_list(request)
        for template in templates:
            flavor_name = template.flavor_name
            flavor = filter(lambda fl: fl.name == flavor_name, flavors)[0]
            self.template_infos[template.name] = \
                "%s vcpu, %s Mb RAM, %s Gb disk" % (
                flavor.vcpus, flavor.ram, flavor.disk)

    name = forms.CharField(
        label=_("Cluster name"),
        required=True)

    base_image = forms.ChoiceField(
        label=_("Base image"),
        required=True)

    hadoop_cluster_topology = forms.ChoiceField(
        label=_("Hadoop cluster topology"),
        required=True,
        choices=[("Single-node master", "Single-node master")]
                 #("Multi-node master", "Multi-node master")]
    )

    jt_nn_template_choices = forms.ChoiceField(
        required=False
    )

    jt_template_choices = forms.ChoiceField(
        required=False
    )

    nn_template_choices = forms.ChoiceField(
        required=False
    )

    worker_template_choices = forms.ChoiceField(
        required=False
    )

    JT_OPT_CHOICES = (("heap_size", "heap_size"),
                      ("dfs.datanode.port", "dfs.datanode.port"),
                      ("dfs.info.port", "dfs.info.port"),
                      ("mapred.job.tracker.info.port",
                       "mapred.job.tracker.info.port"))
    jt_opts = forms.ChoiceField(
        required=False,
        choices=JT_OPT_CHOICES
    )

    NN_OPT_CHOICES = (("heap_size", "heap_size"),
                      ("dfs.datanode.port", "dfs.datanode.port"),
                      ("dfs.info.port", "dfs.info.port"),
                      ("mapred.job.tracker.info.port",
                       "mapred.job.tracker.info.port"))
    nn_opts = forms.ChoiceField(
        required=False,
        choices=NN_OPT_CHOICES
    )

    TT_OPT_CHOICES = (("heap_size", "heap_size"),
                      ("dfs.datanode.port", "dfs.datanode.port"),
                      ("dfs.info.port", "dfs.info.port"),
                      ("mapred.job.tracker.info.port",
                       "mapred.job.tracker.info.port"))
    tt_opts = forms.ChoiceField(
        required=False,
        choices=TT_OPT_CHOICES
    )

    DN_OPT_CHOICES = (("heap_size", "heap_size"),
                      ("dfs.datanode.port", "dfs.datanode.port"),
                      ("dfs.info.port", "dfs.info.port"),
                      ("mapred.job.tracker.info.port",
                       "mapred.job.tracker.info.port"))
    dn_opts = forms.ChoiceField(
        required=False,
        choices=DN_OPT_CHOICES
    )

    result_field = forms.CharField(
        required=True
    )

    def populate_base_image_choices(self, request, context):
        public_images, _more = glance.image_list_detailed(request)
        return [(image.id, image.name) for image in public_images
                if ("image.final" in image.name
                    or "hadoop" in image.name
                    or "hdp" in image.name)]

    def get_help_text(self):
        extra = {}
        extra["template_infos"] = self.template_infos
        return super(GeneralConfigurationAction, self).get_help_text(extra)

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
            return create_cluster(
                request,
                context["name"],
                context["base_image"],
                context["templates"],
            )

        except:
            exceptions.handle(request)
            return False


class SetNameFlavorTypeAction(workflows.Action):
    name = forms.CharField(
        label=_("Node Template Name"),
        required=True)

    flavor_id = forms.ChoiceField(
        label=_("Flavor"),
        required=True)

    NODE_TYPE_CHOICES = (("JT+NN", "JT+NN"),
                         #("NN", "NN"),
                         #("JT", "JT"),
                         ("TT+DN", "TT+DN"))

    node_type = forms.ChoiceField(
        label=_("Nodes type"),
        required=True,
        choices=NODE_TYPE_CHOICES)

    JT_REQUIRED_OPTS = (("heap_size", "heap_size"),)
    JT_OPT_CHOICES = (
        ("dfs.datanode.port", "dfs.datanode.port"),
        ("dfs.info.port", "dfs.info.port"),
        ("mapred.job.tracker.info.port", "mapred.job.tracker.info.port"))

    jt_opts = forms.ChoiceField(
        required=False,
        choices=JT_OPT_CHOICES
    )
    jt_required_opts = forms.ChoiceField(
        required=False,
        choices=JT_REQUIRED_OPTS
    )

    NN_REQUIRED_OPTS = (("heap_size", "heap_size"),)
    NN_OPT_CHOICES = (
        ("dfs.datanode.port", "dfs.datanode.port"),
        ("dfs.info.port", "dfs.info.port"),
        ("mapred.job.tracker.info.port", "mapred.job.tracker.info.port"))

    nn_opts = forms.ChoiceField(
        required=False,
        choices=NN_OPT_CHOICES
    )
    nn_required_opts = forms.ChoiceField(
        required=False,
        choices=NN_REQUIRED_OPTS
    )

    TT_REQUIRED_OPTS = (("heap_size", "heap_size"),)
    TT_OPT_CHOICES = (("dfs.info.port", "dfs.info.port"),)

    tt_opts = forms.ChoiceField(
        required=False,
        choices=TT_OPT_CHOICES
    )
    tt_required_opts = forms.ChoiceField(
        required=False,
        choices=TT_REQUIRED_OPTS
    )

    DN_REQUIRED_OPTS = (("heap_size", "heap_size"),)
    DN_OPT_CHOICES = (("dfs.info.port", "dfs.info.port"),)

    dn_opts = forms.ChoiceField(
        required=False,
        choices=DN_OPT_CHOICES
    )
    dn_required_opts = forms.ChoiceField(
        required=False,
        choices=DN_REQUIRED_OPTS
    )

    template_result_field = forms.CharField(required=False)

    class Meta:
        name = _("Template properties")
        help_text_template = ("project/hadoop/_template_general_help.html")

    def populate_flavor_id_choices(self, request, context):
        flavors = api.nova.flavor_list(request)
        flavor_list = [(flavor.name, flavor.name)
                       for flavor in flavors]
        return flavor_list


class SetNameFlavorType(workflows.Step):
    action_class = SetNameFlavorTypeAction
    contributes = ("name", "flavor_id", "node_type", "options")

    def contribute(self, data, context):
        context["name"] = data.get('name')
        context["flavor_id"] = data.get('flavor_id')
        context["node_type"] = data.get('node_type')
        context["options"] = json.loads(data.get('template_result_field'))
        return context


class CreateNodeTemplate(workflows.Workflow):
    slug = "create_node_template"
    name = _("Create Node Template")
    finalize_button_name = _("Create")
    success_message = _("Created")
    failure_message = _("Could not create")
    success_url = "horizon:project:hadoop:index"
    default_steps = (SelectProjectUser, SetNameFlavorType)

    def handle(self, request, context):
        try:
            name = context["name"]
            node_type = context["node_type"]
            flavor_id = context["flavor_id"]
            jt_opts = context["options"]["jt"]
            nn_opts = context["options"]["nn"]
            tt_opts = context["options"]["tt"]
            dn_opts = context["options"]["dn"]

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
