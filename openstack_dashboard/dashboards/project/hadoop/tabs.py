from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from ehoclient import get_cluster

from openstack_dashboard import api
#from tables import ClusterNodesTable

class DetailTab(tabs.Tab):
    name = _("Details")
    slug = "details_tab"
    template_name = ("project/hadoop/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        cluster = get_cluster(self.tab_group.kwargs['cluster_id'])
        return {"cluster": cluster}

class NodesTab(tabs.TableTab):
    name = _("Nodes")
    slug = "nodes_tab"
#    table_class = ClusterNodesTable
    template_name = ("project/hadoop/_nodes_overview.html")

class ClusterDetailTabs(tabs.TabGroup):
    slug = "cluster_details"
    tabs = (DetailTab,)
    sticky = True
