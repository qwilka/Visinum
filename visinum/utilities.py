import copy
import collections
import logging
import os

logger = logging.getLogger(__name__)



def rupdate(target, src):
    """Recursively update target dict with src. 
    Like «deepupdate» but only merging dictionaries 
    («deepupdate» copyright Ferry Boender, MIT license.)
    (lists and sets are replaced, not merged).
    Ref: https://www.electricmonk.nl/log/2017/05/07/merging-two-python-dictionaries-by-deep-updating/
    """
    for k, v in src.items():
        #if type(v) == dict:
        if isinstance(v, collections.Mapping):
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                rupdate(target[k], v)
        else:
            target[k] = copy.deepcopy(v)


def filepath_valid_test(filePath):
    # https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
    if os.path.exists(filePath):
        retVal = True
    elif os.access(os.path.dirname(filePath), os.W_OK):
        retVal = True
    else:
        retVal = False
    return retVal
