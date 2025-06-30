import zlib
import hashlib
import os
from repository import repository_file

class GitObject (object):
    def __init__(self, data = None):
        if data != None:
            self.deserialize(data)
        else: self.init()

    def serialize(self, repo):
        raise Exception("Unimplemented!")

    def deserialize(self, data):
        raise Exception("Unimplemented!")

    def init(self):
        pass

class GitBlob(GitObject):
    format = b'blob'

    def serialize(self, repo):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data

class GitCommit(GitObject):
    format = b'commit'

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)
    
    def init(self):
        self.kvlm = dict()

# GitTree, GitTag.

def object_read(repository, sha):
    path = repository_file(repository, "objects", sha[0:2], sha[2:])
    
    if not os.path.isfile(path):
        return None

    with open(path, "rb") as file:
        raw = zlib.decompress(file.read())
        x = raw.find(b' ')
        y = raw.find(b'\x00', x)
        format = raw[ 0 : x ]
        size = int(raw[ x : y ].decode("ascii"))

        if size != len(raw) - y - 1:
            raise Exception(f"Malformed object {sha}: bad lenght")

        match format:
            case b'commit'  :   c = GitCommit
            case b'tree'    :   c = GitTree
            case b'tag'     :   c = GitTag
            case b'blob'    :   c = GitBlob
            case _: raise Exception(f"Unknow type {format.decode("ascii")} for object {sha}")

        return c(raw[y + 1 :])

def object_write(object, repository = None):
    data = object.serialize()
    result = object.format + b' ' + str(len(data)).encode() + b'\x00' + data
    sha = hashlib.sha1(result).hexdigest()

    if repository:
        path = repository_file(repository, "objects", sha[0 : 2], sha[2 :], mkdir = True)

        if not os.path.exists(path):
            with open(path, 'wb') as file:
                file.write(zlib.compress(result))

    return sha

def object_find(repository, name, format = None, follow = True):
    return name

def object_hash(find, format, repository = None):
    data = find.read()

    match format:
        case b'commit'  :   object = GitCommit(data)
        case b'tree'    :   object = GitTree(data)
        case b'tag'     :   object = GitTag(data)
        case b'blob'    :   object = GitBlob(data)
        case _: raise Exception(f"Unknown type {format}!")

    return object_write(object, repository)

def kvlm_parse(raw, start = 0, dct = None):
    if not dct:
        dct = dict()

    space = raw.find(b' ', start)
    new_line = raw.find(b'\n', start)

    # Base case
    if (space < 0) or (new_line < space):
        assert new_line == start
        dct[None] = raw[start + 1 :]
        return dct
    
    # Recursive case
    key = raw[start : space]
    end = start

    while True:
        end = raw.find(b'\n', end + 1)
        if raw[end + 1] != ord(' '): break

    value = raw[space + 1 : end].replace(b'\n ', b'\n')

    if key in dct:
        if type(dct[key]) == list:
            dct[key].append(value)
        else: dct[key] = [dct[key], value]
    
    else: dct[key] = value

    return kvlm_parse(raw, start = end + 1, dct = dct)

def kvlm_serialize(kvlm):
    return_value = b''

    for k in kvlm.keys():
        if k == None: continue

        val = kvlm[k]

        if type(val) != list:
            val = [val]
        
        for v in val:
            return_value += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'
    
    return_value += b'\n' + kvlm[None]

    return return_value