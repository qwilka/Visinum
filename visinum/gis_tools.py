import json
import logging
import pathlib
import re
#import os

logger = logging.getLogger(__name__)

import geojson
import numpy as np
from osgeo import ogr, osr

#from ..dtm.bbox_ops import bbox_to_pbox
#from ..tools.vn_file import filepath_valid_test
from .bbox_operations import bbox_union



def geojsonFeature_to_FC(geojFeatureFiles, fc_path, bbox=False, props=None):
    _Featurelist = []
    if bbox:
        bbox_fc = [float("Inf"), float("Inf"), -float("Inf"), -float("Inf")]
    for geojFFile in geojFeatureFiles:
        _pp = pathlib.Path(geojFFile)
        with _pp.open() as fh:
            _Feature = geojson.load(fh)
        if props and isinstance(props, dict):
            _Feature.properties.update(props)
        if bbox and "bbox" in _Feature.properties:
            bbox_fc = bbox_union(bbox_fc, _Feature.properties["bbox"])
        _Featurelist.append(_Feature)
    _FC = geojson.FeatureCollection(_Featurelist)
    if bbox and bbox_fc[0] != float("Inf"):
        _FC["bbox"] = bbox_fc
    _pp = pathlib.Path(fc_path)
    with _pp.open(mode='w') as fh:
        geojson.dump(_FC, fh)
    return True




def EPSG_sting2int(CRS):
    if isinstance(CRS, int):
        return CRS
    elif isinstance(CRS, str) and CRS.strip().upper().startswith("EPSG:"):
        _epsg = CRS.split(":")[1]
        _epsg = int(_epsg)
        return _epsg


def points_change_projection(point, sourceEPSG, targetEPSG="EPSG:4326"):
    """ point is either a single point in a tuple or list: (x, y)
    or point is a list/tuple of points: [(x1,y1), (x2,y2), ...]
    """
    _srcEPSG = EPSG_sting2int(sourceEPSG)
    _tgtEPSG = EPSG_sting2int(targetEPSG)
    if 1<len(point)<=3 and isinstance(point[0], (float, int)):
        _pointsList = [point]
        _single_point = True
    elif (isinstance(point, (list, tuple)) and
            isinstance(point[0], (list, tuple)) and
            1<len(point[0])<=3 ):
        _pointsList = point  # NOTE should check if list/tuple contents are points!
        _single_point = False
    else:
        logger.error("points_change_projection: point not correctly specified: %s" % (str(point),) )
        return False 
    # https://pcjericks.github.io/py-gdalogr-cookbook/projection.html#create-projection
    _source = osr.SpatialReference()
    _source.ImportFromEPSG(_srcEPSG) # http://spatialreference.org/ref/epsg/ed50-utm-zone-32n/
    _target = osr.SpatialReference()
    _target.ImportFromEPSG(_tgtEPSG) # http://spatialreference.org/ref/epsg/wgs-84/
    _transform = osr.CoordinateTransformation(_source, _target)
    transformedList = []
    for _point in _pointsList:      
        # https://pcjericks.github.io/py-gdalogr-cookbook/geometry.html#create-a-point
        _pt = ogr.Geometry(ogr.wkbPoint)
        _pt.AddPoint(*_point)
        _pt.Transform(_transform)
        transformedList.append(_pt.GetPoint_2D())
    if _single_point:
        _returnVal = transformedList[0]
    else:
        _returnVal = transformedList
    return _returnVal


