import collections
import copy
from datetime import datetime, timezone
import json
import logging
import operator

logger = logging.getLogger(__name__)

from vntree import Node, NodeAttr

from . import config, database

__all__ = ["VnNode", "DbCollNode"]


class VnNode(Node):
    _id = NodeAttr()
    db_uri = NodeAttr("vn")

    def __init__(self, name=None, parent=None, data=None, treedict=None):
        super().__init__(name, parent, data, treedict)
        self.data = collections.defaultdict(dict, self.data)

    def get_data(self, *keys, db_load=False):
        if db_load:
            self.db_load()
        if not keys:
            #return copy.deepcopy(self.data)
            _val = self.data
        _datadict = self.data
        for _key in keys:
            _val = _datadict.get(_key, None)
            if isinstance(_val, dict):
                _datadict = _val
            else:
                break
        if isinstance(_val, dict):
            _val = copy.deepcopy(_val)
        if _val is None and not db_load:
            _val = self.get_data(*keys, db_load=True)
        return _val

    def set_data(self, *keys, value, update=False, db_load=False):
        # Note that «value» is a keyword-only argument
        if db_load:
            self.db_load()
        _datadict = self.data
        for ii, _key in enumerate(keys):
            if ii==len(keys)-1:
                if update and isinstance(value, dict) and isinstance(_datadict[_key], dict):
                    _datadict[_key].update(value)
                else:
                    _datadict[_key] = value
            else:
                if _key not in _datadict:
                    _datadict[_key] = {}
                _datadict = _datadict[_key]
        retVal = True
        if db_load:
            retVal = self.db_update()
        return retVal


    def to_treedict(self, recursive=True, full=True):
        if full:
            _dct = {k:v for k, v in vars(self).items() if k not in ["parent", "childs"]}
        else:
            _dct = collections.defaultdict(dict)
            _dct["data"]["vn"] = self.get_data("vn")
            _dct["name"] = self.name
            _dct["_id"] = self._id
        if recursive and self.childs:
            _dct["childs"] = []
            for _child in self.childs:
                _dct["childs"].append( _child.to_treedict(recursive=recursive) )
        return _dct 


    def db_delete(self, recursive=False):
        if recursive:
            retval = list(map(operator.methodcaller('db_delete', recursive=False), self))
            retval = retval[0]
        else:
            _db_uri = config.get_db_uri(**self.db_uri)
            retval = database.db_operation(_db_uri, 'find_one_and_delete')
            logger.debug('%s.db_delete %s' % (self.__class__.__name__, str(_db_uri)))
            if retval:
                retval = retval["_id"]
        return retval 


    def db_insert(self, recursive=False):
        if recursive:
            retval = list(map(operator.methodcaller('db_insert', recursive=False), self))
            retval = retval[0]
        else:
            _db_uri = config.get_db_uri(**self.db_uri)
            self.set_data("vn", "timestamp", value=datetime.now(timezone.utc))
            _doc = self.get_data()
            if "_id" not in _doc:
                _doc["_id"] = _db_uri["_id"]
            if self.childs:
                _doc["childs"] = []
                for _child in self.childs:
                    _doc["childs"].append(_child._id)
            _doc["parent"] = self.parent and self.parent._id
            try:
                retval = database.db_operation(_db_uri, 'insert_one', document=_doc)
            except database.DuplicateKeyError as err:
                logger.error('%s.db_insert %s; %s' % (self.__class__.__name__, str(_db_uri), err))
                return False
            logger.debug('%s.db_insert %s' % (self.__class__.__name__, str(_db_uri)))
            retval = retval.inserted_id
        return retval 


    def db_update(self, timestamp=False):
        _db_uri = config.get_db_uri(**self.db_uri)
        if timestamp:
            self.set_data("vn", "timestamp", value=datetime.now(timezone.utc))
        _doc = self.get_data()
        if "_id" not in _doc:
            _doc["_id"] = _db_uri["_id"]
        if self.childs:
            _doc["childs"] = []
            for _child in self.childs:
                _doc["childs"].append(_child._id)
        try:
            retval = database.db_operation(_db_uri, 'update_one', 
                        update={"$set": _doc},
                        upsert=True)
        except database.DuplicateKeyError as err:
            logger.error('%s.db_insert %s; %s' % (self.__class__.__name__, str(_db_uri), err))
            return False
        logger.debug('%s.insert %s' % (self.__class__.__name__, str(_db_uri)))
        return retval.acknowledged 


    def db_load(self, recursive=False):
        # if not self.db_uri.get("_id", None):
        #     return None
        if recursive:
            _dsdoc = list(map(operator.methodcaller('db_load', recursive=False), self))
            _dsdoc = _dsdoc[0]
        else:
            # if not self.db_uri:
            #     print(self.data)
            _db_uri = config.get_db_uri(**self.db_uri)
            _dsdoc = database.find_by_id(_db_uri)
            if not _dsdoc:
                logger.error('%s.db_load cannot find db document %s' % (self.__class__, str(_db_uri)))
                return False
            for _key, _val in _dsdoc.items():
                if _key in ["parent", "childs", "_id", "db_uri"]:
                    continue
                if _key in self.data: # no clobber, only merge dicts
                    if isinstance(self.data[_key], dict) and isinstance(_val, dict):
                        _val.update(self.data[_key])
                    else:
                        continue
                self.set_data(_key, value=_val)
        return _dsdoc






class DbCollNode(VnNode):
    def __init__(self, db_uri, parent=None):
        _db_uri = config.get_db_uri(**db_uri)
        _ditm_doc = database.find_by_id(_db_uri)
        if not _ditm_doc:
            logger.error('%s.__init__ cannot find db document for %s' % (self.__class__.__name__,str(_db_uri)))
            raise ValueError('{}.__init__ cannot find db document.'.format(self.__class__.__name__))
        super().__init__(_ditm_doc.get("name", None), parent, {"vn":_ditm_doc.get("vn", {})})
        self.db_uri = _db_uri
        for _child_id in _ditm_doc.get("childs", []):
            _db_uri = copy.copy(db_uri)
            _db_uri["_id"] = _child_id
            self.__class__(_db_uri, self)








if __name__ == "__main__":
    pass

