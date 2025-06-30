import sys
from ..repository import repository_find
from ..objects import object_read, object_find

def cmd_cat_file(args):
    repository = repository_find()
    cat_file(repository, args.object, format = args.type.encode())

def cat_file(repository, object, format = None):
    object = object_read(repository, object_find(repository, object, format = format))
    sys.stdout.buffer.write(object.serialize())