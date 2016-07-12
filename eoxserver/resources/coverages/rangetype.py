#-------------------------------------------------------------------------------
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Stephan Krause <stephan.krause@eox.at>
#          Stephan Meissl <stephan.meissl@eox.at>
#          Martin Paces <martin.paces@eox.at>
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

from django.db import transaction
from eoxserver.contrib import gdal
from eoxserver.resources.coverages.models import (
    RangeType, Band, NilValueSet, NilValue,
)

def getAllRangeTypeNames():
    """Return a list of identifiers of all registered range-types."""
    return [item.name for item in RangeType.objects.all()]


def isRangeTypeName(name):
    """
    Check whether there is (``True``) or is not (``False``) a registered
    range-type with given identifier``name``.
    """
    return RangeType.objects.filter(name=name).count() > 0


def getRangeType(name):
    """
    Return range type ``name`` as JSON serializable dictionary.
    The values are loaded from the DB. If there is no ``RangeType``
    record corresponding to the given name ``None`` is returned.
    """
    try:
        # get range-type record
        range_type = RangeType.objects.get(name=name)

        # loop over band records (ordering set in model)
        output_bands = []
        for band in range_type.bands.all():
            output_nil_values = []
            if band.nil_value_set:
                # loop over nil values
                for nil_value in band.nil_value_set.nil_values.all():
                    # append created nil-value dictionary
                    output_nil_values.append({
                        'reason': nil_value.reason,
                        'value': nil_value.raw_value,
                    })

            output_band = {
                'name': band.name,
                'data_type': gdal.GDT_TO_NAME.get(band.data_type, 'Invalid'),
                'identifier': band.identifier,
                'description': band.description,
                'definition': band.definition,
                'uom': band.uom,
                'nil_values': output_nil_values,
                'color_interpretation': gdal.GCI_TO_NAME.get(
                    band.color_interpretation, 'Invalid'
                ),
            }

            if band.raw_value_min is not None:
                output_band["value_min"] = band.raw_value_min
            if band.raw_value_max is not None:
                output_band["value_max"] = band.raw_value_max

            # append created band dictionary
            output_bands.append(output_band)

        # return a JSON serializable dictionary
        return {'name': range_type.name, 'bands': output_bands}

    except RangeType.DoesNotExist:
        return None


def setRangeType(input_range_type):
    """
    Insert range type to the DB. The range type record is
    defined by the ``input_range_type`` which is a dictionary as returned by
    ``getRangeType()`` or parsed form JSON.
    """
    # check the input's data type
    if not isinstance(input_range_type, dict):
        raise ValueError("Invalid input object type!")

    # create record
    try:
        transaction_func = transaction.atomic
    except:
        transaction_func = transaction.commit_on_success

    with transaction_func():
        range_type = RangeType.objects.create(name=input_range_type['name'])

        # compatibility with the old range-type JSON format
        global_data_type = input_range_type.get('data_type', None)

        for idx, band in enumerate(input_range_type['bands']):
            # convert strings to GDAL codes
            data_type = gdal.NAME_TO_GDT[(
                # compatibility with the old range-type JSON format
                global_data_type if global_data_type else band['data_type']
            ).lower()]
            color_interpretation = gdal.NAME_TO_GCI[band[
                # compatibility with the old range-type JSON format
                'gdal_interpretation' if 'gdal_interpretation' in band else
                'color_interpretation'
            ].lower()]

            # prepare nil-value set
            if band['nil_values']:
                nil_value_set = NilValueSet.objects.create(
                    name="__%s_%2.2d__" % (input_range_type['name'], idx),
                    data_type=data_type
                )

                for nil_value in band['nil_values']:
                    NilValue.objects.create(
                        reason=nil_value['reason'],
                        raw_value=str(nil_value['value']),
                        nil_value_set=nil_value_set,
                    )
            else:
                nil_value_set = None

            Band.objects.create(
                index=idx,
                name=band['name'],
                identifier=band['identifier'],
                data_type=data_type,
                description=band['description'],
                definition=band['definition'],
                uom=band['uom'],
                color_interpretation=color_interpretation,
                range_type=range_type,
                nil_value_set=nil_value_set,
                raw_value_min=band.get("value_min"),
                raw_value_max=band.get("value_max")
            )
