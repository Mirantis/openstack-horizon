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
from __future__ import absolute_import

import functools
import logging
import urlparse

from django.utils.decorators import available_attrs

from balancer import client as balancer_client
from balancer.common import exception as balancer_exception
from horizon.api.base import APIDictWrapper, url_for

LOG = logging.getLogger(__name__)


def balancerclient(request):
    o = urlparse.urlparse(url_for(request, 'image'))
    #LOG.debug('balancer connection created for host "%s:%d"' %
    #                       (o.hostname, o.port))
    return balancer_client.Client("127.0.0.1",
                                8181,
                                auth_tok=request.user.token)


class LoadBalancer(APIDictWrapper):
    """
    Wrapper around glance image dictionary to make it object-like and provide
    access to image properties.
    """
    _attrs = ['name', 'algorithm', 'protocol', 'trasport',
             'status', 'created', 'id', 'updated',  'device_id',  'deployed',  'nodes']
             
    def set(self,  attrname,  value):
        self._apidict[attrname] = value

    def __getattr__(self, attrname):
        if attrname == "properties":
            if not hasattr(self, "_properties"):
                properties_dict = super(LoadBalancer, self).__getattr__(attrname)
              
            return self._properties
        else:
            #LOG.debug('Called get attr on LoadBalancer: %s' % attrname)
            return super(LoadBalancer, self).__getattr__(attrname)
            
class Node(APIDictWrapper):
    """
    Wrapper around glance image dictionary to make it object-like and provide
    access to image properties.
    """
    _attrs = ['name', 'address', 'vm_instance', 'state','status', 
             'id', 'deployed',  'nodes']

    def __getattr__(self, attrname):
        if attrname == "properties":
            if not hasattr(self, "_properties"):
                properties_dict = super(Node, self).__getattr__(attrname)
              
            return self._properties
        else:
            #LOG.debug('Called get attr on LoadBalancer: %s' % attrname)
            return super(Node, self).__getattr__(attrname)

def balancer_get_algorithms(request):
    return balancerclient(request).get_algorithms()
    
def balancer_get_probes(request):
     return balancerclient(request).get_probe_types()

def balancer_get_loadbalancer(request,  lb_id):
    
    return LoadBalancer(balancerclient(request).get_loadbalancer(lb_id))
    
def balancer_get_loadbalancers(request):
    lb_list = balancerclient(request).get_loadbalancers()
    lbs = [LoadBalancer(lb) for lb in lb_list]
    return lbs

def balancer_get_balancers_with_VM(request,  vm_id):
    lb_list = balancerclient(request).get_balancers_with_vm(vm_id)
    lbs = [LoadBalancer(lb) for lb in lb_list]
    return lbs
    
def balancer_create_lb(request,  body):
    return balancerclient(request).create_lb(body)
    
def balancer_get_nodes_of_lb(request,  lb_id):
    node_list = balancerclient(request).get_nodes_for_lb(lb_id) 
    nodes = [Node(node) for node in node_list]
    return nodes

def balancer_get_devices(request):
    return balancerclient(request).get_devices()

def balancer_activate_vmnode_in_lbs(request,  node_id,  lb_id_list):
    return balancerclient(request).activate_vmnode_in_lbs(node_id,  lb_id_list)
    
def balancer_suspend_vmnode_in_lbs(request,  node_id,  lb_id_list):
    return balancerclient(request).suspend_vmnode_in_lbs(node_id,  lb_id_list)
    
def balancer_activate_vmnode(request,  node_id):
    return balancerclient(request).activate_vmnode(node_id)
    
def balancer_suspend_vmnode(request,  node_id):
    return balancerclient(request).suspend_vmnode(node_id)
       
def balancer_remove_vmnode_from_lbs(request,  node_id,  lb_id_list):
     return balancerclient(request).remove_vmnode_from_lbs(node_id,  lb_id_list)
    
def balancer_add_vmnode_to_lb(request,  vmnode,  lb_id):
    return balancerclient(request).add_vmnode_to_lb(vmnode,  lb_id)
    
def balancer_delete_lb(request,  lb_id):
    return balancerclient(request).delete_lb(lb_id)

def balancer_get_sticky_list(request):
    return balancerclient(request).get_sticky_list()

def balancer_add_probe_to_lb(request, probe,  lb_id):
    return balancerclient(request).add_probe_to_lb(probe,  lb_id)

def balancer_add_sticky_to_lb(request,  sticky,  lb_id):
     return balancerclient(request).add_sticky_to_lb(sticky,  lb_id)
