#!/usr/bin/python

import os, sys, getopt

from rules import SIXMOZ_rules
from logger import SIXMOZ_logger

## @brief print usage
def usage():
    print "Usage: ./this_script Path [-v|-d] [--dryrun] [-h|--help] [-W] [-I header_from_idl_folder]"

## @brief print help
def _help():
    print "Usage: ./this_script Path [-v|-d] [--dryrun] [-h|--help] [-W]"
    print "-v:\t\tVerbose"
    print "-d:\t\tDebug (Include Verbose)"
    print "--dryrun:\tPerforms a Dryrun (no changes)"
    print "-W:\t\tAdd " + SIXMOZ_rules.get_conf('to_add') + " to all NS_IMETHOD (won't compile)"
    print "-I folder:\tFolder you want to get headers generated from idl_files"
    print "-h --help:\tPrint this Menu"
    print "Path:\t\tFolder you want to add " + SIXMOZ_rules.get_conf('to_add')

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
        try:
            opts, args = getopt.getopt(sys.argv[2:], "I:hvdW", ["help", "dryrun"])
        except getopt.GetoptError as err:
            print str(err)
            usage()
            sys.exit(2)
        except:
            print "Unknown opt Error"
            sys.exit(2)

        if (len(args)):
            print("Unhandled Option")
            sys.exit(1)
        for o, a in opts:
            if o == "-v":
                print "[Running Verbose Mode]"
                SIXMOZ_logger.set_verbose()
            elif o in ("-d"):
                print "[Running Debug Mode]"
                SIXMOZ_logger.set_debug()
            elif o in ("-W"):
                print "[Running UNSAFE Mode]"
                achtung = 1
            elif o in ("-I"):
                print "[Using Idl Folder] " + a
                idl_folder = a
            elif o in ("-h", "--help"):
                _help()
                sys.exit()
            elif o in ("--dryrun"):
                print "[Running DryRun Mode]"
                SIXMOZ_logger.set_dryrun()
            else:
                print("Unhandled Option")
                sys.exit(1)
        return (sys.argv[1], idl_folder, achtung)

    path, idl_folder, achtung = check_options()
