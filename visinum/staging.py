import copy
import fnmatch
import logging
import os
import pathlib
import shutil
import zipfile

logger = logging.getLogger(__name__)

from .vn_uri2 import make_vn_URI
from .metadata import meta_to_vn_metafile


def ast_to_stgdir(ast_meta, stgroot=None, ast_roodir=False, meta_file=False):
    _meta = copy.deepcopy(ast_meta)
    _meta.update( make_vn_URI(**ast_meta, return_dict=True) ) 
    ast_fname = _meta["ast_fname"]
    vn_fname = _meta["vn_fname"]
    if ast_roodir:
        if vn_fname.startswith(ast_fname):
            _uri = vn_fname[len(ast_fname):]
        else:
            _uri = vn_fname
        _uri = _uri.lstrip("_")
        _meta["stg_rpath"] = f"{ast_fname}/{_uri}"
    else:
        _meta["stg_rpath"] = vn_fname
    if stgroot and os.path.isdir(stgroot):
        stgroot_pp = pathlib.Path(stgroot)
        stgdir_pp = stgroot_pp / _meta["stg_rpath"]
        stgdir_pp.mkdir(mode=0o755, parents=True, exist_ok=True)
        _meta["stgdir"] = str(stgdir_pp)
    if meta_file:
        _meta["meta_fpath"] = meta_to_vn_metafile(_meta, stgdir_pp)
        # if isinstance(meta_file, str):
        #     meta_pp = stgdir_pp / meta_file
        # else:
        #     meta_pp = stgdir_pp / "vn-meta.json"
        # with open(meta_pp, 'w') as jfile:
        #     json.dump(_meta, jfile, default=str)
    return _meta


def preclean_files(dir, patt):
    dir_pp = pathlib.Path(dir)
    if isinstance(patt, str):
        patt = [patt]
    delList = []
    for _pattern in patt:
        # if (dir_pp / _pattern).isdir():
        #     shutil.rmtree((dir_pp / _pattern), ignore_errors=True)
        #     continue
        delList.extend(dir_pp.glob(_pattern))
    for _delf in delList:
        if _delf.is_dir():
            shutil.rmtree(_delf, ignore_errors=True)
        else:
            _delf.unlink()
    return delList


def is_staged_dir(stgdir, stgroot):
    stgdir_pp = pathlib.Path(stgdir)
    stgroot_pp = pathlib.Path(stgroot)
    if stgdir_pp==stgroot_pp:
        return False
    if not stgdir_pp.is_dir():
        return False
    try:
        stgdir_pp.relative_to(stgroot_pp)
    except ValueError:
        return False
    return True


def srcdir_to_staging(srcdir, stgroot, srcpatt=None, preclean=False):
    srcdir_pp = pathlib.Path(srcdir)
    stgroot_pp = pathlib.Path(stgroot)
    if not srcdir_pp.is_dir():  #  or not stgroot_pp.is_dir()
        logger.error("srcdir_to_staging: args not correctly specified: srcdir=«%s» stgdir=«%s»" % (srcdir, stgroot))
        return False
    stgdir = stgroot_pp / srcdir_pp.name
    if preclean and is_staged_dir(stgdir, stgroot):
        logger.info("srcdir_to_staging: preclean «%s»" % (stgdir, ))
        shutil.rmtree(stgdir, ignore_errors=True)
    dst = shutil.copytree(srcdir_pp, stgdir)
    return dst



def source_files_to_staging(srcdir, srcpatt, stgdir, preclean=False, 
    clobber=True, includezip=False, zippatt=None):
    srcdir_pp = pathlib.Path(srcdir)
    if stgdir is None:
        stgdir_pp = pathlib.Path(srcdir)
    else:
        stgdir_pp = pathlib.Path(stgdir)
    #srcFiles = srcdir_pp.glob(srcpatt) 
    if srcdir_pp != stgdir_pp:
        stgdir_pp.mkdir(mode=0o755, parents=True, exist_ok=True)
    if preclean:
        delFiles = preclean_files(stgdir_pp, srcpatt)
    srcFiles = []
    tgtFiles = []
    if isinstance(srcpatt, str):
        srcpatt = [srcpatt]
    if isinstance(srcpatt, (list, tuple)):
        for _patt in srcpatt:
            try:
                srcFiles.extend( list(srcdir_pp.glob(_patt)) )
            except Exception as err:
                logger.warning("source_files_to_staging: srcdir_pp.glob(_patt) failed with _patt=«%s»; %s" % (_patt, err))
    for _file in srcFiles:
        if not clobber and _file.is_file():
            continue
        _fpath = shutil.copy(_file, stgdir_pp)
        tgtFiles.append( pathlib.Path(_fpath))
    #tgtFiles = list(stgdir_pp.glob(srcpatt))
    if includezip:
        _flist = zip_files_to_staging(srcdir, srcpatt, stgdir, zippatt, 
            preclean=False, clobber=clobber)
        tgtFiles.extend(_flist)
    return tgtFiles


def zip_files_to_staging(srcdir, srcpatt, stgdir, zippatt=None, 
    preclean=False, clobber=True):
    srcdir_pp = pathlib.Path(srcdir)
    if stgdir is None:
        stgdir_pp = pathlib.Path(srcdir)
    else:
        stgdir_pp = pathlib.Path(stgdir)  
    if srcdir_pp != stgdir_pp:
        stgdir_pp.mkdir(mode=0o755, parents=True, exist_ok=True)
    if preclean:
        delFiles = preclean_files(stgdir_pp, srcpatt)
    zipFiles = []
    if zippatt is None:
        zipFiles.extend( list(srcdir_pp.glob("*.zip")) )
        zipFiles.extend( list(srcdir_pp.glob("*.ZIP")) )
    if isinstance(zippatt, str):
        zippatt = [zippatt]
    if isinstance(zippatt, (list, tuple)):
        for _patt in zippatt:
            try:
                zipFiles.extend( list(srcdir_pp.glob(_patt)) )
            except Exception as err:
                logger.warning("zip_files_to_staging: srcdir_pp.glob(_patt) failed with _patt=«%s»; %s" % (_patt, err))
    if isinstance(srcpatt, str):
        srcpatt = [srcpatt]
    tgtFiles = []
    for zfile in zipFiles:
        _zf = zipfile.ZipFile(zfile, mode='r')
        _zlist = _zf.infolist()
        for patt in  srcpatt:
            # modify srcpatt to work with fnmatch (different from glob)
            _spatt = patt[3:] if patt.startswith("**/") else patt
            for _zinfo in _zlist:
                match = fnmatch.fnmatch(_zinfo.filename, _spatt)
                if match:
                    if not clobber and (stgdir_pp / _zinfo.filename).is_file():
                        continue
                    _ext = _zf.extract(_zinfo, stgdir_pp)
                    _ext = pathlib.Path(_ext)
                    tgtFiles.append(_ext)
        _zf.close()
    return tgtFiles



def make_server_path(svr_dirpath, svr_root):
    root_pp = pathlib.Path(svr_root) 
    if svr_dirpath.startswith("/"): # convert to relative path, if necessary
        svr_dirpath = svr_dirpath[1:]
    dirpath_pp = root_pp / svr_dirpath
    dirpath_pp.mkdir(mode=0o755, parents=True, exist_ok=True)
    return dirpath_pp


def staging_files_to_server(svr_dirpath, filesList, svr_root, cleanPatt=None):
    root_pp = pathlib.Path(svr_root) 
    if svr_dirpath.startswith("/"): # convert to relative path, if necessary
        svr_dirpath = svr_dirpath[1:]
    dirpath_pp = root_pp / svr_dirpath
    dirpath_pp.mkdir(mode=0o755, parents=True, exist_ok=True)
    if cleanPatt:
        delFiles = preclean_files(dirpath_pp, cleanPatt)
    for _file in filesList:
        shutil.copy(_file, dirpath_pp)
    return str(dirpath_pp)

