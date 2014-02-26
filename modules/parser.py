#!/usr/bin/python

import sys
import CppHeaderParser

from logger import SIXMOZ_logger
from rules import SIXMOZ_rules
from options import SIXMOZ_options
from writer import SIXMOZ_writer
import parser_func

class SIXMOZ_parser():
    def __init__(self, files, idl_files):
        self.classes = {}
        self.files = files
        self.idl_files = idl_files
        CppHeaderParser.ignoreSymbols += SIXMOZ_rules.to_ignore

    def init(self):
        self.parse_header_files()
        self.writer = SIXMOZ_writer(self.classes)
        return (self.classes)

    def run(self):
        self.manage_typedefs()
        self.add_full_heritage()
        self.find_override()
        self.writer.run()

    def manage_typedefs(self):
        SIXMOZ_logger.print_info("Stage */6: Managing Typedef's")
        for classname in self.classes:
            for name in self.classes[classname]['typedefs']:
                for nclassname in self.classes:
                    for inh in self.classes[nclassname]['inherits']:
                        if inh == name and self.classes[classname]['typedefs'][name] not in self.classes[nclassname]['inherits']:
                            self.classes[nclassname]['inherits'].append(self.classes[classname]['typedefs'][name])
                            SIXMOZ_logger.print_debug(classname + " typedef inherits: " + self.classes[classname]['typedefs'][name])
                            break

    ## @brief creates the heritage tree for all methods
    ## @param self.classes dict of all self.classes
    #  classname string
    ## @returns void
    def find_override(self):
        SIXMOZ_logger.print_info("Stage 4/6: Finding methods to override")
        for classname in self.classes:
            for j in range(len(self.classes[classname]['inherits'])):
                if (self.classes[classname]['inherits'][j] in self.classes):
                    SIXMOZ_logger.print_debug(classname + " inherits " + self.classes[classname]['inherits'][j])
                    for m in self.classes[self.classes[classname]['inherits'][j]]['meths']:
                        SIXMOZ_logger.print_debug("1: " + self.classes[classname]['inherits'][j] + "::" + self.classes[self.classes[classname]['inherits'][j]]['meths'][m][0])
                        for l in self.classes[classname]['funcs']:
                            SIXMOZ_logger.print_debug("2: " + self.classes[classname]['inherits'][j] + "::" + self.classes[self.classes[classname]['inherits'][j]]['meths'][m][0] \
                                            + " " + classname + "::" + self.classes[classname]['funcs'][l][0])
                            if self.classes[self.classes[classname]['inherits'][j]]['meths'][m][0] == self.classes[classname]['funcs'][l][0]:
                                self.classes[classname]['Ofuncs'][len(self.classes[classname]['Ofuncs'])] = self.classes[classname]['funcs'][l]
                                SIXMOZ_logger.print_debug("OVERRIDE2: " + self.classes[classname]['inherits'][j] + "::" + self.classes[self.classes[classname]['inherits'][j]]['meths'][m][2] \
                                                + " and " + classname + "::" + self.classes[classname]['funcs'][l][2])
                                break
                        for l in self.classes[classname]['meths']:
                            SIXMOZ_logger.print_debug("3: " + self.classes[classname]['inherits'][j] + "::" + self.classes[self.classes[classname]['inherits'][j]]['meths'][m][0] \
                                            + " " + classname + "::" + self.classes[classname]['meths'][l][0])
                            if self.classes[self.classes[classname]['inherits'][j]]['meths'][m][0] == self.classes[classname]['meths'][l][0]:
                                self.classes[classname]['Omeths'][len(self.classes[classname]['Omeths'])] = self.classes[classname]['meths'][l]
                                SIXMOZ_logger.print_debug("OVERRIDE3: " + self.classes[classname]['inherits'][j] + "::" + self.classes[self.classes[classname]['inherits'][j]]['meths'][m][2] \
                                                + " line [" + str(self.classes[self.classes[classname]['inherits'][j]]['meths'][m][3]) + "]" \
                                                + " and " + classname + "::" + self.classes[classname]['meths'][l][2] + " line [" + str(self.classes[classname]['meths'][l][3]) + "]")
                                break

    def add_full_heritage(self):
        SIXMOZ_logger.print_info("Stage 3/6: Creating Heritage Tree")
        self.add_heritage_it()

    def add_heritage_it(self):
        change = 1
        while (change == 1):
            change = 0
            for classname in self.classes:
                add = set(self.classes[classname]['inherits'])
                for simple_inherits in self.classes[classname]['inherits']:
                    if (str(self.classes[classname]['namespace'] + simple_inherits) in self.classes and simple_inherits not in self.classes):
                        simple_inherits = str(self.classes[classname]['namespace'] + simple_inherits)
                    if (simple_inherits in self.classes):
                        for hidden_inherits in self.classes[simple_inherits]['inherits']:
                            if (hidden_inherits in self.classes and hidden_inherits not in self.classes[classname]['inherits'] and hidden_inherits != classname):
                                add.add(hidden_inherits)
                                change = 1
                            else:
                                SIXMOZ_logger.print_debug("OTHER: " + classname + " inherits " + simple_inherits)
                        self.classes[classname]['inherits'] = list(add)

    def parse_header_files(self):
        SIXMOZ_logger.print_info("Stage 2/6: Parsing Header Files")
        nb_files = len(self.files) + len(self.idl_files)
        accessType_tab = [ "public", "private", "protected" ]
        saveout = sys.stdout
        dev_null = open("/dev/null", 'w')
        files = self.files + self.idl_files
        for id_file in range(len(files)):
            try:
                sys.stdout = dev_null
                cppHeader = CppHeaderParser.CppHeader(files[id_file])
                sys.stdout = saveout
                if (SIXMOZ_logger.print_verbose != SIXMOZ_logger.verbose):
                    SIXMOZ_logger.foo_print("[" + str(id_file * 100 / nb_files)  + " %] File: " + files[id_file])
                else:
                    SIXMOZ_logger.print_verbose("[" + str(id_file * 100 / nb_files)  + " %] File: " + files[id_file])
            except CppHeaderParser.CppParseError,  e:
                sys.stdout = saveout
                SIXMOZ_logger.print_error(str(e), files[id_file])
                continue
            except:
                sys.stdout = saveout
                SIXMOZ_logger.print_error("Unknown", files[id_file])
                continue
            SIXMOZ_logger.print_debug("NB CLASSES: " + str(len(cppHeader.classes)))
            SIXMOZ_logger.print_debug(cppHeader.classes)
            for HeaderClass in cppHeader.classes:
                classname = ""
                namespace = ""
                if len(cppHeader.classes[HeaderClass]["namespace"]):
                    namespace = cppHeader.classes[HeaderClass]["namespace"].strip("::") + "::"
                classname += namespace
                classname += cppHeader.classes[HeaderClass]["name"]
                SIXMOZ_logger.print_debug("Class: " + classname)
                if (classname in self.classes and sys.argv[1] in self.classes[classname]['filename']):
                    SIXMOZ_logger.print_debug("Duplicate: " + files[id_file] + " => " + classname)
                    continue
                self.classes[classname] = {}                
                self.classes[classname]['filename'] = files[id_file]
                self.classes[classname]['inherits'] = []
                self.classes[classname]['namespace'] = namespace
                self.classes[classname]['funcs'] = {}
                self.classes[classname]['meths'] = {}
                self.classes[classname]['Ofuncs'] = {}
                self.classes[classname]['Omeths'] = {}
                self.classes[classname]['nested_typedefs'] = {}
                self.classes[classname]['typedefs'] = {}
                for inherit in range(len(cppHeader.classes[HeaderClass]["inherits"])):
                    self.classes[classname]['inherits'].append(cppHeader.classes[HeaderClass]["inherits"][inherit]["class"])
                    SIXMOZ_logger.print_debug("Inherits: " +  self.classes[classname]['inherits'][inherit])
                for accessType in accessType_tab:
                    for id_func in range(len(cppHeader.classes[HeaderClass]["methods"][accessType])):
                        SIXMOZ_logger.print_debug("meth name: " + cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"])
                        SIXMOZ_logger.print_debug("meth ret: " + cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"] \
                                        + " => " + parser_func.check_ret(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"]))
                        SIXMOZ_logger.print_debug(cppHeader.classes[HeaderClass]["methods"][accessType][id_func])
                        meths = parser_func.check_ret(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"])
                        if (len(meths)):
                            meths += " "
                        meths += cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"] + " ("
                        params = ""
                        for param in range(len(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["parameters"])):
                            SIXMOZ_logger.print_debug("meth params: " + cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["parameters"][param]["type"])
                            real_param = cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["parameters"][param]["type"].split("::") 
                            params += real_param[len(real_param) - 1:][0]
                            SIXMOZ_logger.print_debug("Param: " + cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["parameters"][param]["type"] \
                                            + " => " + real_param[len(real_param) - 1:][0])
                            params += " "
                        if (params != "void "):
                            meths += params
                        meths +=  ")"
                        if (cppHeader.classes[HeaderClass]["methods"][accessType][id_func]['const']):
                            meths += " const"
                        if (cppHeader.classes[HeaderClass]["methods"][accessType][id_func].show().find("virtual") != -1) \
                                or (cppHeader.classes[HeaderClass]["methods"][accessType][id_func].show().find("NS_IMETHOD") != -1) \
                                or (cppHeader.classes[HeaderClass]["methods"][accessType][id_func].show().find("NS_IMETHOD_") != -1):
                            if SIXMOZ_options.achtung and ((cppHeader.classes[HeaderClass]["methods"][accessType][id_func].show().find("NS_IMETHOD") != -1) \
                                                or (cppHeader.classes[HeaderClass]["methods"][accessType][id_func].show().find("NS_IMETHOD_") != -1)) \
                                                and ("= 0 ;" not in cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]):
                                self.classes[classname]['Omeths'][len(self.classes[classname]['Omeths'])] = parser_func.over_meth(meths), \
                                    parser_func.over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                                    cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                                    cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                                    cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                            SIXMOZ_logger.print_debug("Meths: " + meths)
                            self.classes[classname]['meths'][len(self.classes[classname]['meths'])] = parser_func.over_meth(meths), \
                                parser_func.over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                        else:
                            SIXMOZ_logger.print_debug("Funcs: " + meths)
                            self.classes[classname]['funcs'][len(self.classes[classname]['funcs'])] = parser_func.over_meth(meths), \
                                parser_func.over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                        SIXMOZ_logger.print_debug(classname + " Funcs(" + str(len(self.classes[classname]['funcs'])) + ") " + " meths(" + str(len(self.classes[classname]['meths'])) + ")")
                self.classes[classname]['nested_typedefs'] = cppHeader.classes[HeaderClass]._public_typedefs
                self.classes[classname]['typedefs'] = cppHeader.typedefs
                for name in cppHeader.classes[HeaderClass]._public_typedefs:
                    SIXMOZ_logger.print_debug("standard: " + cppHeader.classes[HeaderClass]._public_typedefs[name] + " => " + name)
                for l in self.classes[classname]['funcs']:
                    SIXMOZ_logger.print_debug("Func: " + str(l)+ " " + classname + "::" + self.classes[classname]['funcs'][l][0])
                for l in self.classes[classname]['meths']:
                    SIXMOZ_logger.print_debug("Meth: " + str(l)+ " " + classname + "::" + self.classes[classname]['meths'][l][0])
                for name in cppHeader.typedefs:
                    SIXMOZ_logger.print_debug("OTHER: " + cppHeader.typedefs[name] + " => " + name) 
            del cppHeader
        print ""
        dev_null.close()
