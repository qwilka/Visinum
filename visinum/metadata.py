import copy
import json
import logging
import pathlib

logger = logging.getLogger(__name__)


def meta_from_vn_metafile(meta_dirpath, meta_fname="vn-meta.json"):
    meta_dir_pp = pathlib.Path(meta_dirpath)
    if not meta_dir_pp.is_dir():
        logger.error("meta_from_vn_metafile: arg meta_dirpath =«%s» must be a directory." % (meta_dirpath,))
        return None
    meta_fpath_pp = meta_dir_pp / meta_fname
    _meta = {"vn_meta_fpath": None}
    if meta_fpath_pp.is_file():
        with meta_fpath_pp.open() as fh:
            try:
                _meta = json.load(fh)
            except ValueError as err:
                logger.warning("meta_from_vn_metafile: metafile «%s» does not contain valid metadata; %s" % (meta_fpath_pp, err))
    return _meta       


def meta_to_vn_metafile(metadict, meta_dirpath, meta_fname="vn-meta.json", default=str):
    meta_dir_pp = pathlib.Path(meta_dirpath)
    if not meta_dir_pp.is_dir():
        logger.error("meta_to_vn_metafile: arg meta_dirpath =«%s» must be a directory." % (meta_dirpath,))
        return None
    meta_fpath_pp = meta_dir_pp / meta_fname
    # if meta_fpath_pp.is_file():
    #     with meta_fpath_pp.open() as fh:
    #         try:
    #             _meta = json.load(fh)
    #         except ValueError:
    #             _meta = {}
    #     _meta.update(metadict)
    # else:
    #     _meta = copy.deepcopy(metadict)
    _meta = meta_from_vn_metafile(meta_dirpath, meta_fname)
    _meta.update(metadict)
    with open(meta_fpath_pp, 'w') as jfile:
        _meta["vn_meta_fpath"] = str(meta_fpath_pp)
        json.dump(_meta, jfile, default=default)
    return str(meta_fpath_pp)


