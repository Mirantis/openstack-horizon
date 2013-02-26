from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs, tables
from ehoclient import get_cluster, get_cluster_nodes

from openstack_dashboard import api

class DetailTab(tabs.Tab):
    name = _("Details")
    slug = "details_tab"
    template_name = ("project/hadoop/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        cluster = get_cluster(self.tab_group.kwargs['cluster_id'])
        return {"cluster": cluster}

class ClusterNodesTable(tables.DataTable):
    vm_id = tables.Column("vm_id", verbose_name= _("VM id"))
    template_name = tables.Column("template_name", _("Node template name"))

    class Meta:
        name = "cluster_nodes"
        verbose_name = _("Cluster Nodes")


class NodesTab(tabs.TableTab):
    name = _("Nodes")
    slug = "nodes_tab"
    table_classes = (ClusterNodesTable, )
    template_name = ("project/hadoop/_nodes_overview.html")

    def get_cluster_nodes_data(self):
        nodes = get_cluster_nodes(self.tab_group.kwargs['cluster_id'])
        return nodes



class ClusterDetailTabs(tabs.TabGroup):
    slug = "cluster_details"
    tabs = (DetailTab, NodesTab)
    sticky = True
