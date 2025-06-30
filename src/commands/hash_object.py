import sys
from ..repository import repository_find
from ..objects import object_read, object_find, object_hash

def cmd_hash_object(args):
    if args.write:
        repository = repository_find()
    else: repository = None

    with open(args.path, "rb") as find:
        sha = object_hash(find, args.type.encode(), repository)
        print(sha)
    