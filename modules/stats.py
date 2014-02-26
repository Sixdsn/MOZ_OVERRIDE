#!/usr/bin/python

import commands

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
        self.begin = commands.getstatusoutput("find " + SIXMOZ_options.path + SIXMOZ_rules.find_opt + " -or -name \"*.cpp\" | xargs grep " + SIXMOZ_rules.to_add + " | wc -l")[1]


    def display_base(self, classes, files, idl_files):
        tot_meths = 0
        tot_mems = 0

        for i in classes:
            tot_meths += len(classes[i]['funcs'])
            tot_mems += len(classes[i]['meths'])
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
        for classname in classes:
            for k in classes[classname]['Omeths']:
                tmp = classname + "::" +  classes[classname]['Omeths'][k][2]
                if tmp not in self.overrided:
                    if firstprint == 0:
                        firstprint = 1
                        SIXMOZ_logger.print_verbose("NOT OVERRIDED!!!:")
                    virt_missed += 1
                    SIXMOZ_logger.print_verbose(classes[classname]["filename"] + "\t" \
                                  + "M " + tmp + "\t%d" % classes[classname]['Omeths'][k][3])
            for k in classes[classname]['Ofuncs']:
                tmp = classname + "::" + classes[classname]['Ofuncs'][k][2]
                if tmp not in self.overrided:
                    if firstprint == 0:
                        firstprint = 1
                        print_verbose("NOT OVERRIDED!!!:")
                    meth_missed += 1
                    SIXMOZ_logger.print_verbose(classes[classname]["filename"] + "\t" \
                                  + "F " + tmp + "\t%d" % classes[classname]['Ofuncs'][k][3])
        files = []
        for i in classes:
            if classes[i]['filename'] not in files:
                files  += classes[i]['filename']
        self.display_base(classes, files, idl_files)
        SIXMOZ_logger.print_verbose("Final Modified Files: %d" % len(files))
        SIXMOZ_logger.print_verbose("Methods " + SIXMOZ_rules.to_add + " @Begin: " + self.begin)
        SIXMOZ_logger.print_info("Overrided %d methods" % len(set(self.real_overrided)))
        SIXMOZ_logger.print_verbose("Final Modified Meths: %d" % self.modified_meths)
        SIXMOZ_logger.print_verbose("Still Missing %d methods" % virt_missed)
        SIXMOZ_logger.print_verbose("Still Missing %d member functions" % meth_missed)
        output = commands.getstatusoutput("find " + SIXMOZ_options.path + SIXMOZ_rules.find_opt + " -or -name \"*.cpp\" | xargs grep " + SIXMOZ_rules.to_add + " | wc -l")
        SIXMOZ_logger.print_info(SIXMOZ_rules.to_add + " Methods in Code: " + output[1])

        @staticmethod
        def display_class(classe):
            SIXMOZ_logger.print_verbose("File: " + classe['filename'])
            SIXMOZ_logger.print_verbose("Class: " + classname)
            for j in range(len(classe['inherits'])):
                SIXMOZ_logger.print_verbose("From: " + classe['inherits'][j])
            SIXMOZ_logger.print_verbose("Func: %d"% len(classe['funcs']))
            for i in classe['funcs']:
                SIXMOZ_logger.print_verbose(classname + ": " + classe['funcs'][i][0] + " | " + classe['funcs'][i][2])
            SIXMOZ_logger.print_verbose("Meths: %d"% len(classe['meths']))
            for i in classe['meths']:
                SIXMOZ_logger.print_verbose(classname + ": " + classe['meths'][i][0] + " | " + classe['meths'][i][2])
            SIXMOZ_logger.print_verbose("Overrided Func: %d"% len(classe['Ofuncs']))
            for i in classe['Ofuncs']:
                SIXMOZ_logger.print_verbose(classname + ": " + classe['Ofuncs'][i][0])
            SIXMOZ_logger.print_verbose("Overrided Meths: %d"% len(classe['Omeths']))
            for i in classe['Omeths']:
                SIXMOZ_logger.print_verbose(classname + ": " + classe['Omeths'][i][0])
            SIXMOZ_logger.print_verbose("")
