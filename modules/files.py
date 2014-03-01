#!/usr/bin/python

import os, sys, subprocess, string

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

    def __find_idl_files():
        idl_files = []
        if (SIXMOZ_options.idl_folder != ""):
            if (not os.path.exists(SIXMOZ_options.idl_folder)):
                print("Options -I %s doesn't not exist"% SIXMOZ_options.idl_folder)
                sys.exit(1)
            SIXMOZ_logger.print_info("Getting Files from idl_folder: " + SIXMOZ_options.idl_folder)
            idl_files = subprocess.check_output("find " + SIXMOZ_options.idl_folder + 
                                                " -type f -readable \( " +
                                                SIXMOZ_rules.get_conf('extensions') +
                                                " \) -and -not -path \"" +
                                                SIXMOZ_options.path + "*\" | sort", shell=True).decode().split("\n")
        return (idl_files)

    def __find_files():
        SIXMOZ_logger.print_info("Stage 1/6: Getting files to parse: %s"% SIXMOZ_options.path)
        files = subprocess.check_output("find " + SIXMOZ_options.path + " -type f -readable " +
                                        SIXMOZ_rules.get_conf('extensions') +
                                        " -or -name \"*.cpp\" | sort", shell=True).decode().split("\n")
        return (files)

    files = __find_files()
    idl_files = __find_idl_files()

#Only used by override module with multithreading
def get_files():
    return SIXMOZ_files.get_files()

def get_idl_files():
    return SIXMOZ_files.get_idl_files()
