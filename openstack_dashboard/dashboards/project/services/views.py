# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
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
Views for managing Quantum Services.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows

from openstack_dashboard import api
from .tables import AdvancedServicesTable
from .vips.tables import VipsTable
from .workflows import CreateService

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = AdvancedServicesTable
    template_name = 'project/services/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            services = api.quantum.service_list(self.request)
        except:
            services = []
            msg = _('Service list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for n in services:
            n.set_id_as_name_if_empty()
        return services


#class CreateView(workflows.WorkflowView):
#    workflow_class = CreateService
#    template_name = 'project/services/create.html'
#
#    def get_initial(self):
#        pass


#class UpdateView(forms.ModalFormView):
##    form_class = UpdateService
#    template_name = 'project/services/update.html'
#    context_object_name = 'service'
#    success_url = reverse_lazy("horizon:project:services:index")
#
#    def get_context_data(self, **kwargs):
#        context = super(UpdateView, self).get_context_data(**kwargs)
#        context["service_id"] = self.kwargs['service_id']
#        return context
#
#    def _get_object(self, *args, **kwargs):
#        if not hasattr(self, "_object"):
#            service_id = self.kwargs['service_id']
#            try:
#                self._object = api.quantum.service_get(self.request,
#                                                       service_id)
#            except:
#                redirect = self.success_url
#                msg = _('Unable to retrieve service details.')
#                exceptions.handle(self.request, msg, redirect=redirect)
#        return self._object
#
#    def get_initial(self):
#        service = self._get_object()
#        return {'service_id': service['id'],
#                'tenant_id': service['tenant_id'],
#                'name': service['name']}


class DetailView(tables.MultiTableView):
    table_classes = (VipsTable,)
    template_name = 'project/services/detail.html'
    failure_url = reverse_lazy('horizon:project:services:index')

    def get_vips_data(self):
        try:
#            service = self._get_data()
#            vips = api.quantum_services.vip_list(self.request,
#                                              service_id=service.id)
            vips = api.quantum_lb.vip_list(self.request)
        except:
            vips = []
            msg = _('Vip list can not be retrieved.')
            exceptions.handle(self.request, msg)
        for s in vips:
            s.set_id_as_name_if_empty()
        return vips

    def _get_data(self):
        if not hasattr(self, "_service"):
            try:
                service_id = self.kwargs['service_id']
                service = api.quantum.service_get(self.request, service_id)
                service.set_id_as_name_if_empty(length=0)
            except:
                msg = _('Unable to retrieve details for service "%s".') \
                      % (service_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._service = service
        return self._service

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["service"] = self._get_data()
        return context
