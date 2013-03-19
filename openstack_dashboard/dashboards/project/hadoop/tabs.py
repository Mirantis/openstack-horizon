from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse
from django.utils import safestring
from horizon import tabs, tables

from openstack_dashboard.api import glance
from openstack_dashboard.api.eho import get_cluster, get_cluster_nodes, \
    get_node_template


class DetailTab(tabs.Tab):
    name = _("Details")
    slug = "cluster_details_tab"
    template_name = ("project/hadoop/"
                     "_cluster_details_overview.html")

    def get_context_data(self, request):
        cluster = get_cluster(request, self.tab_group.kwargs['cluster_id'])
        base_image_name = glance.image_get(request,
            cluster["base_image_id"]).name
        return {"cluster": cluster, "base_image_name": base_image_name}


class TemplateColumn(tables.Column):
    def get_link_url(self, node_template):
        return reverse(self.link, args=(node_template.template_id,))


class ClusterNodesTable(tables.DataTable):
    vm = tables.Column("vm",
        verbose_name=_("VM info"),
        link=("horizon:project:instances:detail"))
    template_name = TemplateColumn("template_name",
        verbose_name=_("Node template name"),
        link=("horizon:project:hadoop:node_template_details")
    )

    class Meta:
        name = "cluster_nodes"
        verbose_name = _("Cluster Nodes")


class NodesTab(tabs.TableTab):
    name = _("Nodes")
    slug = "nodes_tab"
    table_classes = (ClusterNodesTable, )
    template_name = ("project/hadoop/_nodes_overview.html")

    def get_cluster_nodes_data(self):
        nodes = get_cluster_nodes(self.request,
            self.tab_group.kwargs['cluster_id'])
        return nodes


class ClusterDetailTabs(tabs.TabGroup):
    slug = "cluster_details"
    tabs = (DetailTab, NodesTab)
    sticky = True


class NodeTemplateOverviewTab(tabs.Tab):
    name = _("Details")
    slug = "node_template_details_tab"
    template_name = ("project/hadoop/_node_template_details_overview.html")

    def get_context_data(self, request):
        node_template = get_node_template(request,
            self.tab_group.kwargs['node_template_id'])
        return {"node_template": node_template}


class NodeTemplateDetailsTabs(tabs.TabGroup):
    slug = "node_template_details"
    tabs = (NodeTemplateOverviewTab,)
    sticky = True
