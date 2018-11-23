import logging
#import os
import sys

import visinum

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
lh = logging.StreamHandler()
logger.addHandler(lh)


conf = {
    "database": {
        "host": "localhost",
        "port": 3005,
        "db": "testing"
    },
    "girder": {
        "apiUrl": "http://localhost:8080/api/v1",
        "apiKey": "EdKeaqELS40XIrepHcXZFuLQzrMOGUJOVIeeyR5Z",
    },
}

COLL_TREE =  True

#fs_path = "/home/develop/testdata/L51_dataset_testing"

retVal = visinum.config.initialize(conf=conf)
if retVal:
    logger.info("%s: initialize with config=«%s»" % (__file__,retVal))
else:
    logger.error("%s: failed to initialize." % (__file__,))
    sys.exit(1)



# db_uri = {
#     "db": "testing",
#     "collection": "dataset",
#     "_id": "21362847cf3c3c0ca10e4512d8324855",        
# }
# fs_ds = Dataset2(db_uri=db_uri)
# fs_ds.rootnode = fs_ds.get_tree("fs")

if COLL_TREE:
    # make tree from db collection items
    db_uri = {
        "db": "testing",
        "collection": "fs",
        "_id": "40928e630d643d4ea994bdd185402990",        
    }
    try:
        rootnode = visinum.DbCollNode(db_uri)
    except ValueError as err:
        rootnode = None
        print("{}:{} {} not a valid database document.".format(__file__, err, str(db_uri)) )