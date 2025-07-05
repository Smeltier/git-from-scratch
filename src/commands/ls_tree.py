import sys
import os
from ..repository import repository_find
from ..objects import object_read, object_find, object_hash

def cmd_ls_tree(args):
    repository = repository_find()
    ls_tree(repository, args.tree, args.recursive)

def ls_tree(repository, reference, recursive = None, prefix = ""):
    sha = object_find(repository, reference, format = b'tree')
    object = object_read(repository, sha)

    for item in object.items:
        if len(item.mode) == 5:
            type = item.mode[0 : 1]
        else:
            type = item.mode[0 : 2]

        match type:
            case b'04'  :   type = "tree"
            case b'10'  :   type = "blob"
            case b'12'  :   type = "blob"
            case b'16'  :   type = "commit"
            case _: raise Exception(f"Weird tree leaf mode {item.mode}")

        if not (recursive and type == 'tree'): # a leaf
            print(f"{'0' * (6 - len(item.mode)) + item.mode.decode("ascii")} {type} {item.sha} \t {os.path.join(prefix, item.path)}")
        else: # a branch
            ls_tree(repository, item.sha, recursive, os.path.join(prefix, item.path))
