import copy
import collections
import logging

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
