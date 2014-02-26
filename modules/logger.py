#!/usr/bin/python

import sys

class SIXMOZ_logger():

    @staticmethod
    def __void_write_file(filename, content):
        pass

    @staticmethod
    def __write_file(filename, content):
        fd = file(filename, "w")
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
        print "[DEBUG] ", param

    ## @brief print verbose if "-v" or "-d"
    ## @param param string
    ## @returns void
    @staticmethod
    def verbose(param):
        print "[VERBOSE] ", param

    @staticmethod
    def __void_write_file(filename, content = 0):
        self.print_verbose("[DRYRUN]: " + filename)

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
    def set_dry_run():
        SIXMOZ_logger.dryrun = staticmethod(SIXMOZ_logger.__void_write_file)

    ## @brief print info
    ## @param param string
    ## @returns void
    @staticmethod
    def print_info(param):
        print "[INFO] ", param

    @staticmethod
    def print_error(msg, filename):
        SIXMOZ_logger.print_debug("")
        SIXMOZ_logger.print_debug("[EXCEPTION] " + msg + " " + filename)
        SIXMOZ_logger.file_issue.append(filename)

    file_issue = []
    print_verbose = __void_print
    print_debug = __void_print
    dryrun = __write_file
