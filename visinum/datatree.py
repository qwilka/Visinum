import json
import logging
import pathlib
import os

logger = logging.getLogger(__name__)

from .staging import make_server_path


def make_datatree(datatreeObj):
    svr_root = datatreeObj["svr_root"]
    dirpath_pp = make_server_path(datatreeObj["svr_dirpath"], svr_root)
    ft_items = []
    for _obj in datatreeObj["items"]:
        #_pp = dirpath_pp / _obj["fname"]
        #if _pp.is_file():
        if _obj["type"] == "geojson":
            #dirpath_pp = make_server_path(_obj["svr_dirpath"], svr_root)
            _pp = dirpath_pp / _obj["fname"]
            with open(_pp, 'r') as jfile:
                geoj = json.load(jfile)
            dt_item = {
                "title": _obj["title"],
                "type": "GIS-layer",
                "checkbox": True,
                "selected": False,
                "data": {
                    "layerType": "geojson",
                    "url": os.path.join("/", _pp.relative_to(svr_root))
                }                
            }
            if "bbox" in geoj:
                dt_item["data"]["bbox"] = geoj["bbox"]
            ft_items.append( dt_item )
        elif _obj["type"] == "vn-dtm.nc":
            #dirpath_pp = make_server_path(_obj["svr_dirpath"], svr_root)
            _files = dirpath_pp.glob(_obj["patt"])
            _filesList = []
            for _f in _files:
                _filesList.append(os.path.join("/", _f.relative_to(svr_root)))
            ft_items.append( {
                "title": _obj["title"],
                "type": "DTM-layer",
                "checkbox": True,
                "selected": False,
                "data": {
                    "name": "DTM_test_1m",
                    "tiles": _filesList
                }
            } )
    # if tgtdir:
    #     dirpath_pp = pathlib.Path(tgtdir)
    meta_pp = dirpath_pp / ("datatree-items.ft.json")
    with open(meta_pp, 'w') as jfile:
        json.dump(ft_items, jfile, default=str)
    return ft_items