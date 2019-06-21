"""

Refs:
https://epsg.io/23030
https://spatialreference.org/ref/epsg/4230/
https://github.com/klokantech/epsg.io
http://proj4js.org/
https://github.com/proj4js/proj4js

https://anaconda.org/conda-forge/gdal
https://lengrand.fr/installing-gdal-python36/
https://pcjericks.github.io/py-gdalogr-cookbook/projection.html#reproject-a-geometry
https://fossies.org/dox/gdal-3.0.0/osr_tutorial.html
"""


from osgeo import ogr, osr

def pt_convert_proj(x, y, srcEPSG, tgtEPSG=4326):
    """
    """
    srcSRS = osr.SpatialReference()
    srcSRS.ImportFromEPSG(srcEPSG) 
    tgtSRS = osr.SpatialReference()
    tgtSRS.ImportFromEPSG(tgtEPSG) 
    _transform = osr.CoordinateTransformation(srcSRS, tgtSRS)
    _pt = ogr.Geometry(ogr.wkbPoint)
    _pt.AddPoint(x, y)
    _pt.Transform(_transform)
    tgtpt = _pt.GetPoint_2D()
    return tgtpt


if __name__=="__main__":
    # https://epsg.io/transform#s_srs=23030&t_srs=4230&x=572120.0000000&y=6382750.0000000
    x, y, srcEPSG, tgtEPSG = 572120, 6382750, 23030, 4230
    res = pt_convert_proj(x, y, srcEPSG, tgtEPSG)
    print(f"  E{x}   N{y} EPSG:{srcEPSG} => lon{res[0]:.5f} lat{res[1]:.5f} EPSG:{tgtEPSG}")

    # https://epsg.io/transform#s_srs=4230&t_srs=4326&x=-1.7939917&y=57.5801188
    x, y, srcEPSG, tgtEPSG = res[0], res[1], 4230, 4326
    res = pt_convert_proj(x, y, srcEPSG, tgtEPSG)
    print(f"lon{x:.5f} lat{y:.5f} EPSG:{srcEPSG} => lon{res[0]:.5f} lat{res[1]:.5f} EPSG:{tgtEPSG}")

    # https://epsg.io/transform#s_srs=23030&t_srs=4326&x=572120.0000000&y=6382750.0000000
    x, y, srcEPSG, tgtEPSG = 572120, 6382750, 23030, 4326
    res = pt_convert_proj(x, y, srcEPSG, tgtEPSG)
    print(f"  E{x}   N{y} EPSG:{srcEPSG} => lon{res[0]:.5f} lat{res[1]:.5f} EPSG:{tgtEPSG}")

    # https://pcjericks.github.io/py-gdalogr-cookbook/projection.html#export-projection
    SRS = osr.SpatialReference()
    SRS.ImportFromEPSG(23030)
    params = SRS.ExportToPrettyWkt()
    print(f"EPSG:23030 parameters:\n{params}")
