# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2019 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.files.storage import default_storage as storage

from urlparse import urljoin

from geonode.utils import resolve_object
from geonode.layers.models import Layer, LayerFile

register = template.Library()


@register.simple_tag(takes_context=True)
def original_link_available(context, resourceid, url):

    _not_permitted = _("You are not permitted to save or edit this resource.")

    request = context['request']
    instance = resolve_object(request,
                              Layer,
                              {'pk': resourceid},
                              permission='base.download_resourcebase',
                              permission_msg=_not_permitted)

    download_url = urljoin(settings.SITEURL, reverse("download", args={resourceid}))
    if url != download_url:
        return True

    layer_files = []
    if isinstance(instance, Layer):
        try:
            upload_session = instance.get_upload_session()
            if upload_session:
                layer_files = [
                    item for idx, item in enumerate(LayerFile.objects.filter(upload_session=upload_session))]

                if layer_files:
                    for l in layer_files:
                        if not storage.exists(l.file):
                            return False
        except BaseException:
            return False
    if layer_files:
        return True
    else:
        return False