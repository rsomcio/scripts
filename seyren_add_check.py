#!/bin/env python

import re
import sys
import pymongo
import hashlib
import os
from bson import BSON
from pymongo import Connection

# { "_id" : "5293abe5e4b0355f98716731", "description" : "process", "enabled" : true, "error" : "300000000000", "lastCheck" : null, "live" : true, "name" : "download01 memory leak", "state" : "OK", "target" : "sfly.prod.host.download.download01.processes-java_tomcat.ps_vm.value", "warn" : "250000000000" }

true=bool(1)
false=bool(1)
null=None
connection = Connection('', 27017)
db = connection.seyren
id=hashlib.md5(os.urandom(128)).hexdigest()[:24]
posts = db['checks']
name = '%s.processes-java_tomcat.ps_vm' % sys.argv[1]
target = 'sfly.prod.host.download.%s.value' % name
post = {
    "_id" : id,
    "description" : "process",
    "enabled" : true,
    "error" : "300000000000",
    "lastCheck" : null,
    "live" : true,
    "name" : name,
    "state" : "OK",
    "target" : target,
    "warn" : "250000000000"
}
print post
post_id=posts.insert(post)
count=posts.count()

print "%s %s %s" % (post_id, post,count)

