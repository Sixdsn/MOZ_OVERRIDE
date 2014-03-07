#!/usr/bin/python

import sys
from multiprocessing import Manager

class SIXMOZ_logger():

    rlock = Manager().RLock()

    @staticmethod
    def __my_print(bar):
        with SIXMOZ_logger.rlock:
            print(bar)
            
    @staticmethod
    def __void_write_file(filename, content):
        pass

    @staticmethod
    def __write_file(filename, content):
        fd = open(filename, "w")
        fd.write(content)
        fd.close()

    ## @brief does nothing, called of no "-d" nor "-v"
    ## @param param string
    ## @returns void
    @staticmethod
    def __void_print(param):
        pass

    ## @brief print debug if "-d"
    ## @param param string
    ## @returns void
    @staticmethod
    def __debug(param):
        SIXMOZ_logger.__my_print("[DEBUG] %s"% str(param))

    ## @brief print verbose if "-v" or "-d"
    ## @param param string
    ## @returns void
    @staticmethod
    def verbose(param):
        SIXMOZ_logger.__my_print("[VERBOSE] %s"% str(param))

    @staticmethod
    def __void_write_file(filename, content = 0):
        SIXMOZ_logger.print_verbose("[DRYRUN]: %s"% filename)

    @staticmethod
    def foo_print(bar):
        sys.stdout.write("\r\x1b[K"+bar.__str__())
        sys.stdout.flush()

    @staticmethod
    def __init__():
        pass

    @staticmethod
    def set_verbose():
        SIXMOZ_logger.print_verbose = staticmethod(SIXMOZ_logger.verbose)

    @staticmethod
    def set_debug():
        SIXMOZ_logger.set_verbose()
        SIXMOZ_logger.print_debug = staticmethod(SIXMOZ_logger.__debug)

    @staticmethod
    def set_dryrun():
        SIXMOZ_logger.dryrun = staticmethod(SIXMOZ_logger.__void_write_file)

    ## @brief print info
    ## @param param string
    ## @returns void
    @staticmethod
    def print_info(param):
        SIXMOZ_logger.__my_print("[INFO] %s"% str(param))

    @staticmethod
    def print_error(msg, filename):
        SIXMOZ_logger.print_debug("")
        SIXMOZ_logger.print_debug("[EXCEPTION] " + msg + " " + filename)
        SIXMOZ_logger.file_issue.append(filename)

    file_issue = []
    print_verbose = __void_print
    print_debug = __void_print
    dryrun = __write_file
