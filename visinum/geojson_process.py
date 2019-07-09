import json
import logging
import pathlib
#import re
#import os

logger = logging.getLogger(__name__)

import geojson

from .geo_proj import convert_points_list
from .utilities import filepath_valid_test


def make_lineString(points, srcCRS=None, tgtCRS="EPSG:4326", geojsonFile=None):
   if srcCRS and srcCRS != tgtCRS:
      _pts = convert_points_list(points, srcCRS, tgtCRS)
   else:
      _pts = points
   _linestr = geojson.LineString(_pts)
   if geojsonFile and filepath_valid_test(geojsonFile):
      with open(geojsonFile, 'w') as _geojFile:
         json.dump(_linestr, _geojFile)
   return _linestr


def geojson_to_Feature(geometry, properties=None, geojsonFile=None):
    _Feature = geojson.Feature(geometry=geometry, properties=properties)
    if geojsonFile and filepath_valid_test(geojsonFile):
        with open(geojsonFile, 'w') as _geojFile:
            json.dump(_Feature, _geojFile)
    return _Feature

