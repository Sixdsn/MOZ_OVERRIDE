#!/usr/bin/python

import os, sys, commands, string

from options import SIXMOZ_options
from logger import SIXMOZ_logger
from rules import SIXMOZ_rules

class SIXMOZ_files():
    def __init__(self):
        #besoin d'ajouter check si files est vide ou ['']
        pass

    @staticmethod
    def get_files():
        return (SIXMOZ_files.files)

    @staticmethod
    def get_idl_files():
        return (SIXMOZ_files.idl_files)

    def find_idl_files():
        idl_files = []
        if (SIXMOZ_options.idl_folder != ""):
            if (not os.path.exists(SIXMOZ_options.idl_folder)):
                print("Options -I %s doesn't not exist"% SIXMOZ_options.idl_folder)
                sys.exit(1)
            SIXMOZ_logger.print_info("Getting Files from idl_folder: " + SIXMOZ_options.idl_folder)
            idl_files = string.split(commands.getstatusoutput("find " + SIXMOZ_options.idl_folder + SIXMOZ_rules.find_opt + " | sort")[1], "\n")
        return (idl_files)

    def find_files():
        SIXMOZ_logger.print_info("Stage 1/6: Getting files to parse: %s"% SIXMOZ_options.path)
        files = string.split(commands.getstatusoutput("find " + SIXMOZ_options.path + SIXMOZ_rules.find_opt + " -or -name \"*.cpp\" | sort")[1], "\n")
        return (files)

    files = find_files()
    idl_files = find_idl_files()
