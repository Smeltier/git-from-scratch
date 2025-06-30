from ..repository import repository_create

def cmd_init(args):
    repository_create(args.path)
    print(f"Initialized empty Git repository in {args.path}")
