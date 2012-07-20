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
import urlparse

from django.utils.decorators import available_attrs

from balancerclient.v1 import client as balancer_client

from horizon.api import base


__all__ = ('lb_algorithms_get', 'lb_create', 'lb_delete', 'lb_get',
           'lb_get_for_vm', 'lb_list', 'lb_update', 'node_create',
           'node_delete', 'node_get', 'node_list', 'node_update',
           'probe_create', 'probe_delete', 'probe_get', 'probe_list',
           'sticky_create', 'sticky_delete', 'sticky_get', 'sticky_list')


LOG = logging.getLogger(__name__)
LB_ALGORITHMS = ('RoundRobin', 'LeastConnections', 'LeastLoaded')


def balancerclient(request):
    o = urlparse.urlparse(base.url_for(request, 'loadbalancer'))
    url = "://".join((o.scheme, o.netloc))
    LOG.debug('balancerclient connection created using token "%s" and url "%s"'
              % (request.user.token, url))
    return balancer_client.Client(endpoint=url, token=request.user.token)


# LoadBalancer


def lb_algorithms_get(request):
    return LB_ALGORITHMS


def lb_get(request, lb_id):
    return balancerclient(request).loadbalancers.get(lb_id)


def lb_list(request):
    return balancerclient(request).loadbalancers.list()


def lb_delete(request, lb_id):
    balancerclient(request).loadbalancers.delete(lb_id)


def lb_create(request, name, algorithm, protocol, **extra):
    return balancerclient(request).loadbalancers.create(name, algorithm,
                                                        protocol, **extra)


def lb_update(request, lb_id, name=None, algorithm=None, protocol=None,
              **extra):
    return balancerclient(request).loadbalancers.update(lb_id,
                                                        name=name,
                                                        algorithm=algorithm,
                                                        protocol=protocol,
                                                        **extra)


def lb_get_for_vm(request, vm_id):
    return balancerclient(request).loadbalancers.get_for_vm(vm_id)


# Node


def node_get(request, lb_id, node_id):
    return balancerclient(request).nodes.get(lb_id, node_id)


def node_list(request, lb_id):
    return balancerclient(request).nodes.nodes_for_lb(lb_id)


def node_delete(request, lb_id, node_id):
    balancerclient(request).nodes.delete(lb_id, node_id)


def node_create(request, lb_id, name, type, address, port, weight, status,
                **extra):
    return balancerclient(request).nodes.create(lb_id, name, type, address,
                                                port, weight, status, **extra)


def node_update(request, lb_id, node_id, name=None, type=None, address=None,
                port=None, weight=None, status=None, **extra):
    return balancerclient(request).nodes.update(lb_id, node_id,
                                                name=name,
                                                type=type,
                                                address=address,
                                                port=port,
                                                weight=weight,
                                                status=status,
                                                **extra)


# Probe


def probe_get(request, lb_id, probe_id):
    return balancerclient(request).probes.get(lb_id, probe_id)


def probe_list(request, lb_id):
    return balancerclient(request).probes.probes_for_lb(lb_id)


def probe_delete(request, lb_id, probe_id):
    balancerclient(request).probes.delete(probe_id)


def probe_create(request, lb_id, name, type, **extra):
    return balancerclient(request).probes.create(lb_id, name, type, **extra)


# Sticky


def sticky_get(request, lb_id, sticky_id):
    return balancerclient(request).stickies.get(lb_id, sticky_id)


def sticky_list(request, lb_id):
    return balancerclient(request).stickies.stickies_for_lb(lb_id)


def sticky_delete(request, lb_id, sticky_id):
    balancerclient(request).stickies.delete(lb_id, sticky_id)


def sticky_create(request, lb_id, name, type, **extra):
    return balancerclient(request).stickies.create(lb_id, name, type, **extra)
