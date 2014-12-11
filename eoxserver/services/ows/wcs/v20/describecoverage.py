#-------------------------------------------------------------------------------
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------


from eoxserver.core import Component, implements
from eoxserver.core.decoders import xml, kvp, typelist, upper
from eoxserver.services.ows.interfaces import (
    ServiceHandlerInterface, GetServiceHandlerInterface, 
    PostServiceHandlerInterface
)
from eoxserver.services.ows.wcs.basehandlers import (
    WCSDescribeCoverageHandlerBase
)
from eoxserver.services.ows.wcs.v20.parameters import (
    WCS20CoverageDescriptionRenderParams
)
from eoxserver.services.ows.wcs.v20.util import nsmap


class WCS20DescribeCoverageHandler(WCSDescribeCoverageHandlerBase, Component):
    implements(ServiceHandlerInterface)
    implements(GetServiceHandlerInterface)
    implements(PostServiceHandlerInterface)

    versions = ("2.0.0", "2.0.1")

    index = 5

    def get_decoder(self, request):
        if request.method == "GET":
            return WCS20DescribeCoverageKVPDecoder(request.GET)
        elif request.method == "POST":
            return WCS20DescribeCoverageXMLDecoder(request.body)

    def get_params(self, coverages, decoder):
        return WCS20CoverageDescriptionRenderParams(coverages)


class WCS20DescribeCoverageKVPDecoder(kvp.Decoder):
    coverage_ids = kvp.Parameter("coverageid", type=typelist(str, ","), num=1)


class WCS20DescribeCoverageXMLDecoder(xml.Decoder):
    coverage_ids = xml.Parameter("wcs:CoverageId/text()", num="+")
    namespaces = nsmap
