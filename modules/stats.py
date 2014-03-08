#!/usr/bin/python

import subprocess

from rules import SIXMOZ_rules
from logger import SIXMOZ_logger
from options import SIXMOZ_options

class SIXMOZ_stats():
    mod_files = []
    modified_meths = 0
    real_overrided = []
    overrided = []
    def __init__(self):
        #Number of MOZ_OVERRIDE before launch
        self.begin = subprocess.check_output("find " + SIXMOZ_options.path + " -type f -readable " +
                                             SIXMOZ_rules.get_conf('extensions') + " -or -name \"*.cpp\" | xargs grep " +
                                             SIXMOZ_rules.get_conf('to_add') + " | wc -l", shell=True).decode()

    def display_base(self, classes, files, idl_files):
        tot_meths = 0
        tot_mems = 0

        for cppclass in classes:
            tot_meths += len(cppclass.funcs)
            tot_mems += len(cppclass.meths)
        print("")
        SIXMOZ_logger.print_verbose("Got %d File Issues" % len(SIXMOZ_logger.file_issue))
        for f in SIXMOZ_logger.file_issue:
            SIXMOZ_logger.print_debug(" -> %s"% f)
        SIXMOZ_logger.print_verbose("Found %d files to check" % len(files))
        SIXMOZ_logger.print_verbose("Found %d header files" % len(idl_files))
        SIXMOZ_logger.print_verbose("Found %d classes" % len(classes))
        SIXMOZ_logger.print_verbose("Found %d member functions" % tot_mems)
        SIXMOZ_logger.print_verbose("Found %d methods" % tot_meths)

    def display(self, classes, files, idl_files):
        virt_missed = 0
        meth_missed = 0
        firstprint = 0

        SIXMOZ_logger.print_verbose("")
        SIXMOZ_logger.print_verbose("Statistics")
        for cppclass in classes:
            for classOmeths  in cppclass.Omeths:
                tmp = cppclass.name + "::" +  classOmeths[2]
                if tmp not in self.overrided:
                    if firstprint == 0:
                        firstprint = 1
                        SIXMOZ_logger.print_verbose("NOT OVERRIDED!!!:")
                    virt_missed += 1
                    SIXMOZ_logger.print_verbose(cppclass.filename + "\t" \
                                  + "M " + tmp + "\t%d" % classOmeths[3])
            for classOfuncs in cppclass.Ofuncs:
                tmp = cppclass.name + "::" + classOfuncs[2]
                if tmp not in self.overrided:
                    if firstprint == 0:
                        firstprint = 1
                        SIXMOZ_logger.print_verbose("NOT OVERRIDED!!!:")
                    meth_missed += 1
                    SIXMOZ_logger.print_verbose(cppclass.filename + "\t" \
                                  + "F " + tmp + "\t%d" % classOfuncs[3])

        self.display_base(classes, files, idl_files)
        SIXMOZ_logger.print_verbose("Methods " + SIXMOZ_rules.get_conf('to_add') + " @Begin: " + self.begin)
        SIXMOZ_logger.print_info("Overrided %d methods" % len(set(self.real_overrided)))
        SIXMOZ_logger.print_verbose("Final Modified Meths: %d" % self.modified_meths)
        SIXMOZ_logger.print_verbose("Still Missing %d methods" % virt_missed)
        SIXMOZ_logger.print_verbose("Still Missing %d member functions" % meth_missed)
        output = subprocess.check_output("find " + SIXMOZ_options.path + " -type f -readable " +
                                         SIXMOZ_rules.get_conf('extensions') +
                                         " -or -name \"*.cpp\" | xargs grep " +
                                         SIXMOZ_rules.get_conf('to_add') + " | wc -l", shell=True).decode()
        SIXMOZ_logger.print_info(SIXMOZ_rules.get_conf('to_add') + " Methods in Code: " + output)

def display_class(classe):
    SIXMOZ_logger.print_debug("File: " + classe.filename)
    SIXMOZ_logger.print_debug("Class: " + classe.name)
    for inherit in classe.inherits:
        SIXMOZ_logger.print_debug("From: " + inherit)
    SIXMOZ_logger.print_debug("Func: %d"% len(classe.funcs))
    for classfuncs in classe.funcs:
        SIXMOZ_logger.print_debug(classe.name + ": " + classfuncs[0] + " | " + classfuncs[2])
    SIXMOZ_logger.print_debug("Meths: %d"% len(classe.meths))
    for classmeths in classe.meths:
        SIXMOZ_logger.print_debug(classe.name + ": " + classmeths[0] + " | " + classmeths[2])
    SIXMOZ_logger.print_debug("Overrided Func: %d"% len(classe.Ofuncs))
    for classOfuncs in classe.Ofuncs:
        SIXMOZ_logger.print_debug(classe.name + ": " + classOfuncs[0])
    SIXMOZ_logger.print_debug("Overrided Meths: %d"% len(classe.Omeths))
    for classOmeths in classe.Omeths:
        SIXMOZ_logger.print_debug(classe.name + ": " + classOmeths[0])
    SIXMOZ_logger.print_debug("")
