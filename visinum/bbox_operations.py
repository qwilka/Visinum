import copy
import logging
import numpy as np


logger = logging.getLogger(__name__)


def datum_align(x, base, down=True):
    if down:
        roundfunction = np.floor
    else:
        roundfunction = np.ceil
    try:
        _datum = int(roundfunction(x / base)) * base
    except ZeroDivisionError as err:
        logger.error("datum_align: %s" % (err,) )
        return False
    return _datum



def bbox_to_tilebox(bbox, base):
    minx = datum_align(bbox[0], base, True)
    miny = datum_align(bbox[1], base, True)
    if len(bbox)==4:
        maxx = datum_align(bbox[2], base, False)
        maxy = datum_align(bbox[3], base, False)
        return [minx, miny, maxx, maxy]
    elif len(bbox)==6:
        maxx = datum_align(bbox[3], base, False)
        maxy = datum_align(bbox[4], base, False)
        return [minx, miny, bbox[2], maxx, maxy, bbox[5]]


def bbox_union(bbox1, bbox2):
    _bbox = copy.copy(bbox1)
    bbox_len = (len(bbox1) + len(bbox2)) // 2
    if bbox_len not in (4,6) or any(map(lambda n: not isinstance(n,(int,float)), bbox1+bbox2)):
        logger.error("bbox_union: invalid args «bbox1»=%s «bbox2»=%s" % (bbox1, bbox2))
        return None
    for ii, coord in enumerate(_bbox):
        if ii < bbox_len//2 and bbox2[ii]<_bbox[ii]:
            _bbox[ii] = bbox2[ii]
        elif ii >= bbox_len//2 and bbox2[ii]>_bbox[ii]:
            _bbox[ii] = bbox2[ii]      
    return _bbox


def bbox_to_bbox_pts(bbox):
    if len(bbox)==4:
        return [bbox[:2], bbox[2:]]
    elif len(bbox)==6:
        return [bbox[:3], bbox[3:]]

def bbox_pts_to_bbox(bbox):
    return bbox[0] + bbox[1]
