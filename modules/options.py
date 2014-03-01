#!/usr/bin/python

import os, sys, getopt

from rules import SIXMOZ_rules
from logger import SIXMOZ_logger

## @brief print usage
def usage():
    print("Usage: ./this_script Path [-v|-d] [--dryrun] [-h|--help] [-W] [-I header_from_idl_folder] [-J Number of parallel parsers]")

## @brief print help
def _help():
    print("Usage: ./this_script Path [-v|-d] [--dryrun] [-h|--help] [-W]")
    print("-v:\t\tVerbose")
    print("-d:\t\tDebug (Include Verbose)")
    print("--dryrun:\tPerforms a Dryrun (no changes)")
    print("-W:\t\tAdd %s to all NS_IMETHOD (won't compile)"% SIXMOZ_rules.get_conf('to_add'))
    print("-I folder:\tFolder you want to get headers generated from idl_files")
    print("-h --help:\tPrint this Menu")
    print("Path:\t\tFolder you want to add %s"% SIXMOZ_rules.get_conf('to_add'))

class SIXMOZ_options():
    @staticmethod
    def __init__():
        pass

    def check_options():
        if (len(sys.argv) < 2 or len(sys.argv[1]) <= 0 or not os.path.exists(sys.argv[1])):
            usage()
            sys.exit(1)
        idl_folder = ""
        achtung = 0
        workers = 1
        try:
            opts, args = getopt.getopt(sys.argv[2:], "hdvWJ:I:", ["help", "dryrun"])
        except getopt.GetoptError as err:
            print("GetOpt Error: %s"% str(err))
            usage()
            sys.exit(2)
        except:
            print("Unknown opt Error")
            sys.exit(2)

        if (len(args)):
            print("Unhandled Option")
            sys.exit(1)
        for o, a in opts:
            if o == "-v":
                print("[Running Verbose Mode]")
                SIXMOZ_logger.set_verbose()
            elif o in ("-d"):
                print("[Running Debug Mode]")
                SIXMOZ_logger.set_debug()
            elif o in ("-W"):
                print("[Running UNSAFE Mode]")
                achtung = 1
            elif o in ("-I"):
                print("[Using Idl Folder] %s"% a)
                idl_folder = a
            elif o in ("-J"):
                if (int(a) <= 0):
                    usage()
                    sys.exit(1)
                print("[Using %d Workers]"% int(a))
                workers = int(a)
            elif o in ("-h", "--help"):
                _help()
                sys.exit(0)
            elif o in ("--dryrun"):
                print("[Running DryRun Mode]")
                SIXMOZ_logger.set_dryrun()
            else:
                print("Unhandled Option")
                sys.exit(1)
        return (sys.argv[1], idl_folder, achtung, workers)

    path, idl_folder, achtung, workers = check_options()
