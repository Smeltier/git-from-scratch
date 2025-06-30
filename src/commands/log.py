import sys
from ..repository import repository_find
from ..objects import object_find, object_read

def cmd_log(args):
    repo = repository_find()

    print("digraph wyaglog{")
    print("  node[shape=rect]")
    log_graph_vizualize(repo, object_find(repo, args.commit), set())
    print("}")

def log_graph_vizualize(repo, sha, seen):
    if sha in seen:
        return
    seen.add(sha)

    commit = object_read(repo, sha)
    message = commit.kvlm[None].decode("utf8").strip()
    message = message.replace("\\", "\\\\")
    message = message.replace("\"", "\\\"")

    if "\n" in message:
        message = message[:message.index("\n")]

    print(f"  c_{sha} [label=\"{sha[0:7]}: {message}\"]")
    assert commit.format == b'commit'

    if not b'parent' in commit.kvlm.keys():
        return

    parents = commit.kvlm[b'parent']

    if type(parents) != list:
        parents = [ parents ]

    for p in parents:
        p = p.decode("ascii")
        print (f"  c_{sha} -> c_{p};")
        log_graph_vizualize(repo, p, seen)