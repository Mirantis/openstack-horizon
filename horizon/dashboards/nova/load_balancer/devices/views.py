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

"""
Views for managing Nova instances.
"""
import logging

from django import http
from django import shortcuts
from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response

from horizon import api
from horizon import exceptions
from horizon import forms
from horizon import tabs
from .forms import Add_DeviceForm,  AddProbe,  AddSticky
from .tabs import InstanceDetailTabs


LOG = logging.getLogger(__name__)
class AddProbeView(forms.ModalFormView):
      form_class = AddProbe
      template_name = 'nova/load_balancer/devices/addprobe.html'
      context_object_name = 'balancer'
      
      def get_form_kwargs(self):
        LOG.debug("Init Add Probe view from kwargs")
        kwargs = super(AddProbeView, self).get_form_kwargs()
        kwargs['probe_list'] = self.probe_list()
        instance_id = self.kwargs['balancer_id']
        #self.object = api.server_get(self.request, instance_id)
        kwargs['balancer'] = self.object
        return kwargs
        
      def probe_list(self):
        try:
            LOG.debug("Retrieve probe list")
            probes_list = api.balancer_get_probes(self.request)
            probe_type = [(x, x) for x in probes_list]
           
        except:
            probes_list = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instance algorithms.'))
        return sorted(probe_type)

            
      def get_object(self, *args, **kwargs):
        if not hasattr(self, "object"):
            balancer_id = self.kwargs['balancer_id']
            try:
                self.object = api.balancer_get_loadbalancer(self.request,  balancer_id)
            except:
                redirect = reverse("horizon:nova:load_balancer:index")
                msg = _('Unable to retrieve instance details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self.object
        
      def get_initial(self):
        return {'id': self.kwargs['balancer_id'],
                'tenant_id': self.request.user.tenant_id,
                'name': getattr(self.object, 'name', '')}
    

class AddStickyView(forms.ModalFormView):
      form_class = AddSticky
      template_name = 'nova/load_balancer/devices/addsticky.html'
      context_object_name = 'balancer'
      
      def get_form_kwargs(self):   
            LOG.debug("Init Add sticky view from kwargs")
            kwargs = super(AddStickyView, self).get_form_kwargs()
            kwargs['sticky_list'] = self.sticky_list()
            instance_id = self.kwargs['balancer_id']
            #self.object = api.server_get(self.request, instance_id)
            kwargs['balancer'] = self.object
            return kwargs
            
      def sticky_list(self):
        try:
            LOG.debug("Retrieve sticky list")
            sticky_list = api.balancer_get_sticky_list(self.request)
            sticky_type = [(x, x) for x in sticky_list]
           
        except:
            sticky_list = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instance algorithms.'))
        return sorted(sticky_type)

            
      def get_object(self, *args, **kwargs):
        if not hasattr(self, "object"):
            balancer_id = self.kwargs['balancer_id']
            try:
                self.object = api.balancer_get_loadbalancer(self.request,  balancer_id)
            except:
                redirect = reverse("horizon:nova:load_balancer:index")
                msg = _('Unable to retrieve instance details.')
                exceptions.handle(self.request, msg, redirect=redirect)
        return self.object
        
      def get_initial(self):
        return {'id': self.kwargs['balancer_id'],
                'tenant_id': self.request.user.tenant_id,
                'name': getattr(self.object, 'name', '')}
        

class Add_DeviceView(forms.ModalFormView):
    form_class = Add_DeviceForm
    template_name = 'nova/load_balancer/devices/add_device.html'
    
    def get_form_kwargs(self):
        LOG.debug("Init Load Balancer View from kwargs")
        kwargs = super(Add_DeviceView, self).get_form_kwargs()
        kwargs['algorithm_list'] = self.algorithm_list()
        kwargs['probes_list'] = self.probes_list()
        kwargs['rservers_list'] = self.rservers_list()
        kwargs['device_list'] = self.device_list()
        
        return kwargs
        
    def algorithm_list(self):
        try:
            LOG.debug("Retrieving algorithm list")
            algorithm_list = api.balancer_get_algorithms(self.request)
            algorithm_types = [ (x, x) for x in algorithm_list]
        except:
            algorithm_list = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instance algorithms.'))
        return sorted(algorithm_types)
        
    def probes_list(self):
        try:
            LOG.debug("Retrieve probe list")
            probes_list = api.balancer_get_probes(self.request)
            probe_type = [(x, x) for x in probes_list]
           
        except:
            probes_list = []
            exceptions.handle(self.request,
                              _('Unable to retrieve instance algorithms.'))
        return sorted(probe_type)
        
    def rservers_list(self):
        # Gather our instances
        rservers =[]
        try:
            LOG.debug("Retrieve instance list")
            instances = api.server_list(self.request)
        except:
            instances = []
            exceptions.handle(self.request, _('Unable to retrieve instances.'))
        # Gather our flavors and correlate our instances to them
        if instances:
            try:
                flavors = api.flavor_list(self.request)
                full_flavors = SortedDict([(str(flavor.id), flavor) for \
                                            flavor in flavors])
                for instance in instances:
                    instance.full_flavor = full_flavors[instance.flavor["id"]]
                    rservers.append((instance.addresses['private'][0]['addr']+','+str(instance.id)+','+str(instance.name), str(instance.name)))
            except:
                msg = _('Unable to retrieve instance size information.')
                exceptions.handle(self.request, msg)
        return rservers
        
    def device_list(self):
        devices=[]
        try:
            LOG.debug("Retrieve device list")
            device_list = api.balancer_get_devices(self.request)
            for dev in device_list:
                devices.append((dev['id'],  dev['name']))
        except:
            msg = _('Unable to retrieve instance size information.')
            exceptions.handle(self.request, msg)
        return devices
            
