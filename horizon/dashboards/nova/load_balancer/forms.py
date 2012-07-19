import logging

from django import shortcuts
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import api
from horizon import exceptions

from balancerclient.common import exceptions as balancerclient_exceptions


LOG = logging.getLogger(__name__)

LB_ALGORITHMS = (
    ('ROUND_ROBIN', 'ROUND_ROBIN'),
    ('LEAST_CONNECTIONS', 'LEAST_CONNECTIONS'),
)

LB_PROTOCOLS = (
    ('HTTP', 'HTTP'),
)


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Load Balancer Name"))
    algorithm = forms.ChoiceField(choices=LB_ALGORITHMS,
                        label=_("Node selection algorithm of load balancing."))
    protocol = forms.ChoiceField(choices=LB_PROTOCOLS,
                                 label=_("Protocol of load balancing."))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_("Port of load balancing."))

    def handle(self, request, data):
        try:
            api.lb_create(request, data['name'], data['algorithm'],
                          data['protocol'], port=data['port'])
            message = "Creating load balancer \"%s\"" % data["name"]
            LOG.info(message)
            messages.info(request, message)
        except balancerclient_exceptions.ClientException, e:
            LOG.exception("ClientException in CreateLoadBalancer")
            messages.error(request,
                           _("Error Creating Load Balancer: %s") % e.message)
        return shortcuts.redirect("horizon:nova:load_balancer:index")


class UpdateForm(forms.SelfHandlingForm):
    lb = forms.CharField(widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}))
    name = forms.CharField(widget=forms.TextInput(
                                        attrs={'readonly': 'readonly'}))
    algorithm = forms.ChoiceField(choices=LB_ALGORITHMS,
                        label=_("Node selection algorithm of load balancing."))
    port = forms.IntegerField(min_value=1, max_value=65536, initial=80,
                              label=_("Port of load balancing."))

    def handle(self, request, data):
        try:
            api.lb_update(request, data['lb'], algorithm=data['algorithm'],
                          port=data['port'])
            messages.success(request,
                             _("Load Balancer \"%s\" updated.") % data['name'])
        except:
            exceptions.handle(request, _('Unable to update load balancer.'))
        return shortcuts.redirect('horizon:nova:load_balancer:index')
