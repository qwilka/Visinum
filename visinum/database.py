import logging
#import os
#import sys
logger = logging.getLogger(__name__)

import pymongo 
from bson.objectid import ObjectId
from bson.errors import InvalidId


ExecutionTimeout = pymongo.errors.ExecutionTimeout
DuplicateKeyError = pymongo.errors.DuplicateKeyError



def db_operation(db_uri, operation, **kwargs):
    retval = None
    dbclient = pymongo.MongoClient(db_uri["host"], db_uri["port"])
    db = dbclient[db_uri["db"]]
    dbcoll = db[db_uri["collection"]]
    if operation in ['count', 'find', 'find_one', 'find_one_and_delete',
                     'delete_one', 'delete_many',
                     'update_one', 'replace_one']:
        # http://api.mongodb.com/python/current/api/pymongo/collection.html
        _extra_kwargs = {}
        if "filter" not in kwargs and "_id" in db_uri:
            _extra_kwargs["filter"] = {"_id": db_uri["_id"]}
        retval = getattr(dbcoll, operation)(**kwargs, **_extra_kwargs)
        logger.debug("db_operation: %s returned %s" % (operation, str(retval)[:50]))
    elif operation in ['insert_one', 'insert_many', 'create_index']:
        # http://api.mongodb.com/python/current/api/pymongo/collection.html
        retval = getattr(dbcoll, operation)(**kwargs)
        logger.debug("db_operation: %s returned %s" % (operation, str(retval)[:50]))
    elif operation.__name__ in  ['fstree_to_db', 'dbtree_to_Nodes']:
        retval = operation(dbcoll=dbcoll, **kwargs)
        logger.debug("db_operation: %s returned %s" % (operation.__name__, retval))
    else:
        logger.warning('db_operation operation not available: %s', operation)
    dbclient.close()
    return retval


def find_by_id(db_uri, _id=None):
    if not _id:
        if "_id" in db_uri:
            _id = db_uri["_id"]
        else:
            return False
    dbclient = pymongo.MongoClient(db_uri["host"], db_uri["port"])
    db = dbclient[db_uri["db"]]
    dbcoll = db[db_uri["collection"]] 
    returnVal = dbcoll.find_one(filter={"_id":_id})
    if returnVal is None and isinstance(_id, str):
        try:
            obj_id = ObjectId(_id)
        except InvalidId as err:
            logger.warning("find_by_id: %s; _id=%s; %s" % (str(db_uri), _id, err))
            returnVal = None
        else:
            returnVal = dbcoll.find_one(filter={"_id": obj_id})
    return returnVal



if __name__ == '__main__':  
    pass           