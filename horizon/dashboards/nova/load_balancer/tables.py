import logging

from django import template
from django.utils.translation import ugettext_lazy as _

from horizon import tables


LOG = logging.getLogger(__name__)


def get_enabled(service, reverse=False):
    options = ["Enabled", "Disabled"]
    if reverse:
        options.reverse()
    return options[0] if not service.disabled else options[1]


class ServicesTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_('Id'), hidden=True)
    name = tables.Column("name", verbose_name=_('Name'))
    service_type = tables.Column("type", verbose_name=_('Type'))
    enabled = tables.Column(get_enabled,
                            verbose_name=_('Enabled'),
                            status=True)

    class Meta:
        name = "load_balancer"
        verbose_name = _("Load Balancer")
        table_actions = (ServiceFilterAction,)
        multi_select = False
        status_columns = ["enabled"]
