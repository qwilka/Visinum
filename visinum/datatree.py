import json
import logging
import pathlib
import os
import subprocess

logger = logging.getLogger(__name__)

from scipy.io import netcdf

from .gis_tools import points_change_projection
from .bbox_operations import bbox_to_bbox_pts, bbox_pts_to_bbox
from .staging import make_server_path


def make_datatree(datatreeObj):
    svr_root = datatreeObj["svr_root"]
    dirpath_pp = make_server_path(datatreeObj["svr_dirpath"], svr_root)
    ft_items = []
    rbush_idx_list = []
    for ii, _obj in enumerate(datatreeObj["items"]):
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
                #_filesList.append(os.path.join("/", _f.relative_to(svr_root)))
                _filesList.append(_f.name)
            dt_item = {
                "title": _obj["title"],
                "type": "DTM-layer",
                "checkbox": True,
                "selected": False,
                "data": {
                    "name": "DTM_test_1m",
                    "svr_dir": os.path.join("/", dirpath_pp.relative_to(svr_root)),
                    "tiles": _filesList
                }
            }
            ft_items.append( dt_item )
        elif _obj["type"] == "index":
            _files = dirpath_pp.glob(_obj["patt"])
            rbush_items = []
            for _f in _files:
                if _f.name.endswith(".vn-dtm.nc"):
                    nc = netcdf.netcdf_file(str(_f), mode='r', mmap=False)
                    bbox_UTM = nc.variables['bbox_UTM']
                    SRS = nc.SRS.decode('utf-8')
                    #print(SRS)
                    bbox_pts = points_change_projection(bbox_to_bbox_pts(list(bbox_UTM[:])), SRS)
                    bbox = bbox_pts_to_bbox(bbox_pts)
                    rbush_items.append( {
                        "minX": bbox[0],
                        "minY": bbox[1],
                        "maxX": bbox[2],
                        "maxY": bbox[3],
                        "fname": _f.name                        
                    } )
                    nc.close()
                    print(f"{_f.name} {bbox}")
            dt_item = {
                "title": _obj["title"],
                "type": "DTM-layer",
                "checkbox": True,
                "selected": False,
                "data": {
                    "rbush_items": rbush_items,
                    "svr_dir": os.path.join("/", dirpath_pp.relative_to(svr_root)),
                }
            }
            ft_items.append( dt_item )
            rbush_idx_list.append(ii)
    # if tgtdir:
    #     dirpath_pp = pathlib.Path(tgtdir)
    meta_pp = dirpath_pp / ("datatree-items.ft.json")
    with open(meta_pp, 'w') as jfile:
        json.dump(ft_items, jfile, default=str)
    for _idx in rbush_idx_list:
        rbush_vndtm_files(str(meta_pp), _idx)
    return ft_items



def rbush_vndtm_files(datatree_fpath, datatree_idx,
    rbush_script="/home/develop/engineering/src/visinumjs/examples/rbush_vn-dtm_files.js"
):
    #curr_dir = os.getcwd()
    #curdir_pp = pathlib.Path.cwd()
    rbush_pp = pathlib.Path(rbush_script)
    datatree_pp = pathlib.Path(datatree_fpath)
    metadict = {}
    commandList = [
        'node',
        '-r', 'esm',
        rbush_script,
        str(datatree_fpath),
        str(datatree_idx)
    ]
    metadict["cmd"] = " ".join(commandList)
    try:
        result = subprocess.run(commandList, cwd=rbush_pp.parent, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
        logger.error("rbush_vn-dtm_files: %s" % (err, ) )
        return None
    metadict["cmd_result"] = result.stdout.decode('utf-8')
    meta_pp = datatree_pp.parent / "rbush_vndtm_files.json"
    with open(meta_pp, 'w') as jfile:
        json.dump(metadict, jfile, default=str)
    return metadict

