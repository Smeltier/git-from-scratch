import os
import configparser

class GitRepository (object):
    worktree = None
    gitdirectory = None
    config = None

    def __init__(self, path, force = False):
        self.worktree = path
        self.gitdirectory = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdirectory)):
            raise Exception(f"Not a Git repository {path}")

        self.config = configparser.ConfigParser()
        configfile = repository_file(self, "config")

        if configfile and os.path.exists(configfile):
            self.config.read([configfile])
        elif not force:
            raise Exception("Configuration file missing.")

        if not force:
            version = int(self.config.get("core", "repositoryformatversion"))

            if version != 0:
                raise Exception(f"Unsupported repositoryformatversion: {version}")

def repository_default_config():
    config = configparser.ConfigParser()
    config.add_section("core")
    config.set("core", "repositoryformatversion", "0")
    config.set("core", "filemode", "false")
    config.set("core", "bare", "false")
    
    return config

def repository_path(repository, *path):
    return os.path.join(repository.gitdirectory, *path)

def repository_file(repository, *path, mkdir = False):
    if repository_directory(repository, *path[:-1], mkdir = mkdir):
        return repository_path(repository, *path)
    
    return None 

def repository_directory(repository, *path, mkdir = False):
    path = repository_path(repository, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else: raise Exception(f"Not a directory: {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else: return None

def repository_create(path):
    repository = GitRepository(path, True)

    if os.path.exists(repository.worktree):
        if not os.path.isdir(repository.worktree):
            raise Exception(f"{path} is not a directory!")

        if os.path.exists(repository.gitdirectory) and os.listdir(repository.gitdirectory):
            raise Exception(f"{path} is not empty!")
    else:
        os.makedirs(repository.worktree)

    assert repository_directory(repository, "branches", mkdir = True)
    assert repository_directory(repository, "objects", mkdir = True)
    assert repository_directory(repository, "refs", "tags", mkdir = True)
    assert repository_directory(repository, "refs", "heads", mkdir = True)

    with open(repository_file(repository, "HEAD"), "w") as file:
        file.write("ref: refs/heads/master\n")

    with open(repository_file(repository, "config"), "w") as file:
        config = repository_default_config()
        config.write(file)

    return repository

def repository_find(path = ".", required = True):
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        if required:
            raise Exception("No git directory.")
        else: return None

    return repository_find(parent, required)