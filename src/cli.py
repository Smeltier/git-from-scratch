import argparse
import sys
from .commands import init, cat_file, hash_object, log

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
                                metavar="type",
                                dest="type",
                                choices=["blob", "commit", "tag", "tree"],
                                default="blob",
                                help="Specify the type")
hash_object_parser.add_argument("-w",
                                dest="write",
                                action="store_true",
                                help="Actually write the object into the database")
hash_object_parser.add_argument("path", 
                                help="Read object from <file>") 

log_parser = argsubparsers.add_parser("log", help="Display history of a given commit.")
log_parser.add_argument("commit",
                        default="HEAD",
                        nargs="?",
                        help="Commit to start at.")

def main(argv = sys.argv[1:]):
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