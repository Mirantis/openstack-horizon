import logging

from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import tables


LOG = logging.getLogger(__name__)


class DeleteLoadBalancer(tables.DeleteAction):
    data_type_singular = _("Load Balancer")
    data_type_plural = _("Load Balancers")

    def delete(self, request, lb_id):
        api.lb_delete(request, lb_id)


class LoadBalancersTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ('build',  None),
        ('',  None),
        ('error',  False),
    )
    id = tables.Column("id", verbose_name=_('id'), hidden=True)
    name = tables.Column("name", verbose_name=_('Name'))
    algorithm = tables.Column("algorithm", verbose_name=_("Algorithm"))
    status = tables.Column("status",
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    class Meta:
        name = "loadbalancers"
        verbose_name = _("Load Balancers")
        status_columns = ["status"]
        row_actions = (DeleteLoadBalancer,)
