import sys
import os
from ..repository import repository_find
from ..objects import object_read, object_find

def cmd_checkout(args):
    reposiroty = repository_find()
    object = object_read(reposiroty, object_find(reposiroty, args.commit))

    if object.format == b'commit':
        object = object_read(reposiroty, object.kvlm[b'tree'].decode("ascii"))
    
    if os.path.exists(args.path):
        if not os.path.isdir(args.path):
            raise Exception(f"Not a directory {args.path}!")
        if os.listdir(args.path):
            raise Exception(f"Not empty {args.path}!")
    else:
        os.makedirs(args.path)

    tree_checkout(reposiroty, object, os.path.realpath(args.path))

def tree_checkout(repository, object, path):
    for item in object.items:
        child_object = object_read(repository, item.sha)
        dest = os.path.join(path, item.path)

        if object.format == b'tree':
            os.mkdir(dest)
            tree_checkout(repository, child_object, dest)
        elif object.format == b'blob':
            with open(dest, 'wb') as file:
                file.write(child_object.blobdata)