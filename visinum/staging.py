import logging
import pathlib
import shutil

logger = logging.getLogger(__name__)


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


def source_files_to_staging(srcdir, srcpatt, stgdir, clobber=True):
    srcdir_pp = pathlib.Path(srcdir)
    if stgdir is None:
        stgdir_pp = pathlib.Path(srcdir)
    else:
        stgdir_pp = pathlib.Path(stgdir)
    srcFiles = srcdir_pp.glob(srcpatt) 
    if srcdir_pp != stgdir_pp:
        stgdir_pp.mkdir(mode=0o755, parents=True, exist_ok=True)
        if clobber:
            delFiles = preclean_files(stgdir_pp, srcpatt)
        for _file in srcFiles:
            if not clobber and _file.is_file():
                continue
            shutil.copy(_file, stgdir_pp)
        srcFiles = stgdir_pp.glob(srcpatt)
    return (stgdir_pp, srcFiles)



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

