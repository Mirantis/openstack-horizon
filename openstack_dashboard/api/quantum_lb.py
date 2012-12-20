from __future__ import absolute_import

import logging

from quantumclient.v2_0 import client as quantum_client
from django.utils.datastructures import SortedDict

from openstack_dashboard.api.base import APIDictWrapper, url_for


LOG = logging.getLogger(__name__)

def quantumclient(request):
    LOG.debug('quantumclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, url_for(request, 'network')))
    LOG.debug('user_id=%(user)s, tenant_id=%(tenant)s' %
              {'user': request.user.id, 'tenant': request.user.tenant_id})
    c = quantum_client.Client(token=request.user.token.id,
                              endpoint_url=url_for(request, 'network'))
    return c

class QuantumAPIDictWrapper(APIDictWrapper):

    def set_id_as_name_if_empty(self, length=8):
        try:
            if not self._apidict['name']:
                id = self._apidict['id']
                if length:
                    id = id[:length]
                self._apidict['name'] = '(%s)' % id
        except KeyError:
            pass

    def items(self):
        return self._apidict.items()

class Vip(QuantumAPIDictWrapper):
    _attrs = ['name', 'id', 'tenant_id', 'address', 'port']

def vip_list(request, **params):
    vips = []
    for i in range(10):
        vips.append({'id': 'agsfas%s' % i, 'name': 'vip #%s' % i, 'tenant_id': '123', 'address': '127.0.0.%s' % i, 'port': '100%s' % i})
    return [Vip(n) for n in vips]

def vip_get(request, vip_id):
    i = vip_id
    return Vip({'id': 'agsfas%s' % i, 'name': 'vip #%s' % i, 'tenant_id': '123', 'address': '127.0.0.%s' % i, 'port': '100%s' % i})

def vip_delete(request, vip_id):
    pass


class Member(QuantumAPIDictWrapper):
    _attrs = ['name', 'id', 'tenant_id', 'address', 'port']

def member_list(request, **params):
    members = []
    for i in range(15):
        members.append({'id': 'agsfas%s' % i, 'name': 'member #%s' % i, 'tenant_id': '123', 'address': '10.1.2.%s' % i, 'port': '30%s' % i})
    return [Vip(n) for n in members]

def member_get(request, member_id):
    i = member_id
    return Member(({'id': 'agsfas%s' % i, 'name': 'member #%s' % i, 'tenant_id': '123', 'address': '10.1.2.%s' % i, 'port': '30%s' % i}))

def member_create(request, network_id, cidr, ip_version, **kwargs):
    """
    Create a member for a specified vip
    :param request: request context
    :param network_id: network id a subnet is created on
    :param cidr: subnet IP address range
    :param ip_version: IP version (4 or 6)
    :param gateway_ip: (optional) IP address of gateway
    :param tenant_id: (optional) tenant id of the subnet created
    :param name: (optional) name of the subnet created
    :returns: Subnet object
    """
    body = {'id': 'new'}
    body.update(kwargs)
    return Member(body)

def member_delete(request, member_id):
    pass
