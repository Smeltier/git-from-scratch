import sys
import os
from ..repository import repository_find, reference_list, repository_file
from ..objects import object_read, object_find, object_hash

def cmd_show_ref(args):
    repository = repository_find()
    references = reference_list(repository)

    show_reference(repository, references, prefix = "refs")

def show_reference(repository, references, with_hash = True, prefix = ""):
    if prefix:
        prefix = prefix + '/'
    
    for k, v in references.items():
        if type(v) == str and with_hash:
            print(f"{v} {prefix}{k}")
        elif type(v) == str:
            print(f"{prefix}{k}")
        else:
            show_reference(repository, v, with_hash = with_hash, prefix = f"{prefix}{k}")

def reference_create(repository, reference_name, sha):
    with open(repository_file(repository, "refs/" + reference_name), 'w') as file:
        file.write(sha + "\n")