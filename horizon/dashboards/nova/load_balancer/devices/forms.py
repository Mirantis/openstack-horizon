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

import logging
import json

from django import shortcuts
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse


from horizon import api
from horizon import exceptions
from horizon import forms
from django.forms import IPAddressField, CharField, ChoiceField, Select,  MultipleChoiceField

LOG = logging.getLogger(__name__)

class TriggerSelect(forms.Select):
    class Media:
        js = ('hideHTTPGroup.js')
        
class AddProbe(forms.SelfHandlingForm):
    id = forms.CharField(widget=forms.HiddenInput(
                               attrs={'readonly': 'readonly'}))
    instance_name = forms.CharField(label=_("Instance Name"),  widget=forms.TextInput(attrs={'readonly':'readonly'}))
   
    probe_list = forms.ChoiceField(label="Probe Type", widget=TriggerSelect(attrs={"id":"probeList","OnChange":"hideHTTPGroup(document.getElementById('probeList'))"}))
    probeInterval = forms.CharField(label=_("Interval Between Probes (sec)"),  widget=forms.TextInput(),  initial="15")
    passDetectInterval = forms.CharField(label=_("Probe Timeout"),  widget=forms.TextInput(),  initial="60")
    failDetect = forms.CharField(label=_("Failed Probe Count for Deactivation"),  widget=forms.TextInput(),  initial="3")
    requestMethodType = forms.ChoiceField(label="Probe Type",  choices=(("GET", "GET"),  ("HEAD","HEAD"),   ("POST", "POST")))
    requestHTTPurl = forms.CharField(label=_("HTTP Probe URL"),  widget=forms.TextInput(attrs={"id":"httpURL"}),  initial="/")
    appendPortHostTag = forms.BooleanField(label=_("Append Port to Host"),  initial="True",  required=False)
    minExpectStatus =  forms.CharField(label=_("Minimal Expected Return Code"),  widget=forms.TextInput(attrs={"id":"minCode"}),  initial="200",  required=False)
    maxExpectStatus =  forms.CharField(label=_("Maximal Expecter Return Code"),  widget=forms.TextInput(attrs={"id":"maxCode"}),  initial="500",  required=False)
    
    def __init__(self, *args, **kwargs):
        LOG.debug("Init Add Probe Form for Load Balancers")
        probe_list = kwargs.pop('probe_list')
        self.balancer_obj = kwargs.pop('balancer')        
        super(AddProbe, self).__init__(*args, **kwargs)
        self.fields['instance_name'].initial = self.balancer_obj.name        
        self.fields['probe_list'].choices = probe_list
        
    def handle(self,  request,  data):
        lb_id = data['id']
        probe_list = data['probe_list']
        probe={}
        probe['type'] = data['probe_list']
        probe['probeInterval'] = data['probeInterval']
        probe['passDetectInterval'] = data['passDetectInterval']
        probe['failDetect'] = data['failDetect']
        probe['requestMethodType'] = data['requestMethodType']
        probe['requestHTTPurl'] = data['requestHTTPurl']
        probe['appendPortHostTag'] = data['appendPortHostTag']
        probe['minExpectStatus'] = data['minExpectStatus']
        probe['maxExpectStatus'] = data['maxExpectStatus']
        lb_probe={'healthMonitoring': probe}
        
        api.balancer_add_probe_to_lb(request,  lb_probe,  lb_id)
        messages.success(request,
                         _('New probe was successfully created for %s')%self.balancer_obj.name )        
        return  shortcuts.redirect(
                        'horizon:nova:load_balancer:index')


class AddSticky(forms.SelfHandlingForm):
    id = forms.CharField(widget=forms.HiddenInput(
                               attrs={'readonly': 'readonly'}))
    instance_name = forms.CharField(label=_("Instance Name"),  widget=forms.TextInput(attrs={'readonly':'readonly'}))
   
    sticky_list = forms.ChoiceField(label="Sticky Type", widget=TriggerSelect(attrs={"id":"sticky","OnChange":"hideStickyGroup(document.getElementById('sticky'))"}))

    timeout = forms.CharField(label=_("Timeout (minutes)"),  widget=forms.TextInput(),  initial="5")

    httpURL = forms.CharField(label=_("HTTP URL"),  widget=forms.TextInput(attrs={"id":"httpURL"}),           
              initial="http://cisco.com")
    cookieName = forms.CharField(label=_("Cookie Header"),  widget=forms.TextInput(attrs={"id":"httpCookie"}),           
              initial="SESSIONID")
    headerName = forms.CharField(label=_("HTTP Header"),  widget=forms.TextInput(attrs={"id":"httpHeader"}),           
              initial="SESSIONID")
    netmask =  forms.CharField(label=_("IP Netmask"),  widget=forms.TextInput(attrs={"id":"ipNetmask"}),           
              initial="255.255.255.0")

    def __init__(self, *args, **kwargs):
        LOG.debug("Init Add Sticky Form for Load Balancers")
        sticky_list = kwargs.pop('sticky_list')
        self.balancer_obj = kwargs.pop('balancer')        
        super(AddSticky, self).__init__(*args, **kwargs)
        self.fields['instance_name'].initial = self.balancer_obj.name        
        self.fields['sticky_list'].choices = sticky_list
        
    def handle(self,  request,  data):
        lb_id = data['id']
        sticky_list = data['sticky_list']
        sticky = {}
        sticky['type'] =  data['sticky_list']
        sticky['timeout']  = data['timeout']
        sticky['httpURL'] = data['httpURL']
        sticky['cookieName'] = data['cookieName']
        sticky['headerName'] = data['headerName']
        sticky['netmask'] = data['netmask']
        sticky_entry = {'sessionPersistence' : sticky}
        api.balancer_add_sticky_to_lb(request,sticky_entry,   lb_id)
        messages.success(request,
                         _('New sticky entry was successfully created for %s')%self.balancer_obj.name )
        return  shortcuts.redirect(
                        'horizon:nova:load_balancer:index')

class Add_DeviceForm(forms.SelfHandlingForm):
    method = 'POST'
    device = ChoiceField(label=_("Balancer Device"),  help_text=_("Please select balancing device to deploy config to"))
    lb_name = CharField(label=_("Load Balancer Name"), help_text=_("Name of Load Balancer instance") )
    vip = CharField(label=_("Virtual IP"), help_text=_("Set the IPv4 address"),)
    mask = CharField(label=_("Mask"))
    vip_port = CharField(label=_("VIP Port"),  help_text=_("Incomming port to listen on VIP"))
    vip_VLAN = CharField(label=_("VIP VLAN"),  help_text = _("VLAN Interface to create VIP"))
    vip_protocol = ChoiceField(label=_("Application Protocol"),  choices=(('HTTP', 'HTTP'), ('FTP', 'FTP')))
    vip_transport = ChoiceField(label=_("Transport Protocol"),  choices=(('TCP', 'TCP'), ('UDP', 'UDP')))
    vip_reply_icmp = forms.BooleanField(label=_("Reply on ICMP"))
    algorithm = ChoiceField(label=_("Loadblance Algorithm"),  choices=(), widget=Select())
    rservers = MultipleChoiceField(label=_("Servers in Server Farm"), choices=(), widget=forms.SelectMultiple(attrs={'size':10,'width':'200px'},),  validators=[])
    rs_port = CharField(label=_("Server port"),  help_text=_("Application Port on servers"))
    probes = MultipleChoiceField(label="Attached Health Monitoring Probes", choices=(), widget=forms.CheckboxSelectMultiple(attrs={'size':10,'width':'100px'},  ))
    url = CharField(label = "HTTP Probe URL",  initial="/",  widget=forms.TextInput())
    probe_method = ChoiceField(label="HTTP Probe Method",  choices=(('GET','GET'), ('HEAD', 'HEAD'))) 
    
    def __init__(self, *args, **kwargs):
        LOG.debug("Init Add Device Form for Load Balancers")
        algorithm_list = kwargs.pop('algorithm_list')
        probes_list = kwargs.pop('probes_list')
        rservers_list = kwargs.pop('rservers_list')
        device_list = kwargs.pop('device_list')
        
        super(Add_DeviceForm, self).__init__(*args, **kwargs)
        LOG.debug("Set algorithm choices to list %s" % algorithm_list)
        self.fields['algorithm'].choices = algorithm_list
        LOG.debug("Set probes choices to list %s" % probes_list)
        self.fields['probes'].choices = probes_list
        LOG.debug("Set rservers choices to list %s" % rservers_list)
        self.fields['rservers'].choices = rservers_list
        self.fields['rservers'].required = False
        self.fields['probes'].required = False
        self.fields['device'].choices = device_list
        
        self.fields['vip_reply_icmp'].required = False
        self.fields['url'].required = False
        self.fields['probe_method'].required = False
    
    def handle(self, request, data):
        try:
            LOG.debug("Handling create LB command")
            body ={}
            body['name'] = data['lb_name']
            body['algorithm'] = data['algorithm']
            body['protocol'] = data['vip_protocol']
            body['transport'] = data['vip_transport']
            body['device_id'] = data['device']
            vip = {}
            vip['address'] = data['vip']
            vip['VLAN'] = data['vip_VLAN']
            vip['mask'] = data['mask']
            vip['port'] = data['vip_port']
            vip['ICMPreply'] = data['vip_reply_icmp']
            body['virtualIps'] = [vip]
            nodes = []
            for node in data['rservers']:
                LOG.debug("Processing node %s " "%s" % (node,  type(node)))
                
                nd = node.encode('ascii','ignore')
                nd_data = nd.split(',')

                nodes.append({'address':nd_data[0],  'type':'host', 'port':data['rs_port'],  'vm_instance': nd_data[2],  'vm_id':nd_data[1]})
            body['nodes'] = nodes
            probes=[]
            for probe in data['probes']:
                prob ={}
                prob['type'] = probe
                if probe == 'HTTP':
                    prob['path'] = data['url']
                    prob['method'] = data['probe_method']
                probes.append(prob)
            body['healthMonitor'] = probes;
            lb = api.balancer_create_lb(request,  body)
            messages.success(request,
                         _('Load Balancer "%s" was successfully created') % data["lb_name"])
        except:
            LOG.debug("Some exception occured")
            redirect = reverse("horizon:nova:load_balancer:index")
            exceptions.handle(request,_('Unable to create LB'), redirect=redirect)
        return shortcuts.redirect('horizon:nova:load_balancer:index')
