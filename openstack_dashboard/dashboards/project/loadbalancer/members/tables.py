# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
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

from django.utils.translation import ugettext_lazy as _
from horizon import tables

import logging

LOG = logging.getLogger(__name__)


class MembersTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Name"),
                         link='horizon:project:loadbalancer:members:detail')
    address = tables.Column("address", verbose_name=_("Member Address"))
    port = tables.Column("port", verbose_name=_("TCP Port"))

    class Meta:
        name = "members"
        verbose_name = _("Members")
