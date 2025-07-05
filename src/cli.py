import argparse
import sys

from .commands import init
from .commands import add
from .commands import commit
from .commands import cat_file
from .commands import check_ignore
from .commands import checkout
from .commands import hash_object
from .commands import log
from .commands import ls_files
from .commands import ls_tree
from .commands import rev_parse
from .commands import rm
from .commands import show_ref
from .commands import status
from .commands import tag

argparser = argparse.ArgumentParser(description = "Content tracker")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

init_parser = argsubparsers.add_parser("init", help = "Initialize a new, empty repository.")
init_parser.add_argument("path",
                         metavar = "directory",
                         nargs = "?",
                         default = ".",
                         help = "Where to create the repository.")

cat_file_parser = argsubparsers.add_parser("cat-file", help = "Provide content of repository objects")
cat_file_parser.add_argument("type",
                             metavar = "type",
                             choices = ["blob", "commit", "tag", "tree"],
                             help = "Specify the type")
cat_file_parser.add_argument("object",
                             metavar = "object",
                             help = "The object to display")

hash_object_parser = argsubparsers.add_parser("hash-object", help = "Compute object ID and optionally creates a blob from a file")
hash_object_parser.add_argument("-t",
                                metavar = "type",
                                dest = "type",
                                choices = ["blob", "commit", "tag", "tree"],
                                default = "blob",
                                help = "Specify the type")
hash_object_parser.add_argument("-w",
                                dest = "write",
                                action = "store_true",
                                help = "Actually write the object into the database")
hash_object_parser.add_argument("path", 
                                help = "Read object from <file>") 

log_parser = argsubparsers.add_parser("log", help="Display history of a given commit.")
log_parser.add_argument("commit",
                        default = "HEAD",
                        nargs = "?",
                        help = "Commit to start at.")

list_tree_parser =  argsubparsers.add_parser("ls-tree", help="Pretty-print a tree object.")
list_tree_parser.add_argument("-r",
                   dest="recursive",
                   action="store_true",
                   help="Recurse into sub-trees")

list_tree_parser.add_argument("tree",
                              help = "A tree-ish object")

checkout_parser = argsubparsers.add_parser("checkout", help="Checkout a commit inside of a directory.")
checkout_parser.add_argument("commit",
                             help = "The commit or tree to checkout.")
checkout_parser.add_argument("path",
                             help = "the EMPTY directory to checkout on.")

show_ref_parser = argsubparsers.add_parser("show-ref", 
                                           help = "List references.")

tag_parser = argsubparsers.add_parser("tag",
                                      help="List and create tags")

tag_parser.add_argument("-a",
                        action="store_true",
                        dest="create_tag_object",
                        help="Whether to create a tag object")

tag_parser.add_argument("name",
                        nargs="?",
                        help="The new tag's name")

tag_parser.add_argument("object",
                        default="HEAD",
                        nargs="?",
                        help="The object the new tag will point to")


def main(argv = sys.argv[1 : ]):
    args = argparser.parse_args(argv)
    match args.command:
        case "init"         :   init.cmd_init(args)
        case "add"          :   add.cmd_add(args) 
        case "commit"       :   commit.cmd_commit(args)
        case "cat-file"     :   cat_file.cmd_cat_file(args)
        case "check-ignore" :   check_ignore.cmd_check_ignore(args)
        case "checkout"     :   checkout.cmd_checkout(args)
        case "hash-object"  :   hash_object.cmd_hash_object(args)
        case "log"          :   log.cmd_log(args)
        case "ls-files"     :   ls_files.cmd_ls_files(args)
        case "ls-tree"      :   ls_tree.cmd_ls_tree(args)
        case "rev-parse"    :   rev_parse.cmd_rev_parse(args)
        case "rm"           :   rm.cmd_rm(args)
        case "show-ref"     :   show_ref.cmd_show_ref(args)
        case "status"       :   status.cmd_status(args)
        case "tag"          :   tag.cmd_tag(args)
        case _              :   print("Please, try again.")