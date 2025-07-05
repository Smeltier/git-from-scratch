import zlib
import hashlib
import os
import re
from repository import repository_file, repository_directory, reference_resolve

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

class GitBlob (GitObject):
    format = b'blob'

    def serialize(self, repo):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data

class GitCommit (GitObject):
    format = b'commit'

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)
    
    def init(self):
        self.kvlm = dict()

class GitTreeLeaf (GitObject):

    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha

class GitTree (GitObject):

    format = b'tree'

    def deserialize(self, data):
        self.items = tree_parse(data)

    def serialize(self):
        return tree_serialize(self)
    
    def init(self):
        self.items = list()

class GitTag (GitCommit):
    format = b'tag'

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

def object_resolve(repository, name):
    candidates = list()
    hashRE = re.compile(r"^[0-9A-Fa-f]{4,40}$")

    if not name.strip():
        return None
    
    if name == "HEAD":
        return [reference_resolve(repository, "HEAD")]
    
    if hashRE.match(name):
        name = name.lower()
        prefix = name[0 : 2]
        path = repository_directory(repository, "objects", prefix, mkdir = False)

        if path:
            rem = name[2:]
            for f in os.listdir(path):
                if f.startswith(rem):
                    candidates.append(prefix + f)
    
    as_tag = reference_resolve(repository, "refs/tags/" + name)
    if as_tag:
        candidates.append(as_tag)
    
    as_branch = reference_resolve(repository, "refs/heads/" + name)
    if as_branch:
        candidates.append(as_branch)
    
    as_remote_branch = reference_resolve(repository, "refs/remotes/" + name)
    if as_remote_branch:
        candidates.append(as_remote_branch)
    
    return candidates

def object_find(repository, name, format = None, follow = True):
    sha = object_resolve(repository, name)

    if not sha:
        raise Exception(f"No such reference {name}.");

    if len(sha) > 1:
        raise Exception("Ambiguous reference {name}: Candidates are: \n - {'\n - '.join(sha)}")
    
    sha = sha[0]

    if not format:
        return sha
    
    while True:
        object = object_read(repository, sha)

        if object.format == format:
            return sha;

        if not follow:
            return None
        
        if object.format == b'tag':
            sha = object.kvlm[b'object'].decode("ascii")
        elif object.format == b'commit' and format == b'tree':
            sha = object.kvlm[b'tree'].decode("ascii")
        else:
            return None

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

def tree_parse_one(raw, start = 0):
    x = raw.find(b' ', start)
    assert x - start == 5 or x - start == 6

    mode = raw[start : x]
    if len(mode) == 5:
        mode = b"0" + mode
    
    y = raw.find(b'\x00', x)

    path = raw[x + 1 : y]

    raw_sha = int.from_bytes(raw[y + 1 : y + 21], "big")

    sha = format(raw_sha, "040x")

    return y + 21, GitTreeLeaf(mode, path.decode("utf8"), sha)

def tree_parse(raw):
    position = 0
    max = len(raw)
    ret = list()

    while position < max:
        position, data = tree_parse_one(raw, position)
        ret.append(data)

    return ret

def tree_leaf_sort_key(leaf):
    if leaf.mode.startswith(b"10"):
        return leaf.path
    else:
        return leaf.path + "/"
    
def tree_serialize(object):

    object.items.sort(key = tree_leaf_sort_key)

    return_value = b''

    for i in object.items:

        sha = int(i.sha, 16)

        return_value += i.mode
        return_value += b' '
        return_value += i.path.encode("utf8")
        return_value += b'\x00'
        return_value += sha.to_bytes(20, byteorder = "big")

    return return_value