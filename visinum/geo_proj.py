import logging

logger = logging.getLogger(__name__)

from pyproj import Transformer


def transform_point(point, srcCRS, tgtCRS="EPSG:4326"):
    """
    point (list, tuple): [x, y] 2D only

    Refs:
    https://github.com/pyproj4/pyproj
    """
    x_src, y_src = point
    transformer = Transformer.from_crs(srcCRS, tgtCRS, always_xy=True)
    x_tgt, y_tgt = transformer.transform(x_src, y_src)
    return [x_tgt, y_tgt]


def convert_points_list(pointsList, srcCRS, tgtCRS="EPSG:4326"):
    """Convert points list recusively, preserving original list structure.
    Limited to lists of [x, y] 2D points.
    """
    if not isinstance(pointsList, (list, tuple)) or not isinstance(pointsList[0], (list, tuple)):
        logger.error("convert_points_list: arg pointsList «%s» is not correctly specified; pointsList should be a list of points (or a list of lists))." % (str(pointsList)[:100],))
        return None
    retList = []
    for itm in pointsList:
        if isinstance(itm[0], (float, int)) and len(itm)>=2:
            retVal = transform_point(itm[:2], srcCRS, tgtCRS)
        elif isinstance(itm[0], (list, tuple)):
            retVal = convert_points_list(itm, srcCRS, tgtCRS)
        retList.append(retVal)
    return retList


if __name__ == "__main__":
    l1 = [[[572120, 6382750], [572130, 6382740]], [[572110, 6382730], [572120, 6382720]]]
    l1 = [[572120, 6382750]]
    retVal = convert_points_list(l1, "EPSG:23030", "EPSG:3857")  # "EPSG:3857" "EPSG:4326"
    print(f"{l1} \n {retVal}")
