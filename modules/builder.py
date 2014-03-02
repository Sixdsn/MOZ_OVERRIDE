#!/usr/bin/python

import sys, concurrent.futures, CppHeaderParser

from multiprocessing import Value, Manager
from itertools import izip

from logger import SIXMOZ_logger
from rules import SIXMOZ_rules
from options import SIXMOZ_options
from writer import SIXMOZ_writer
from options import SIXMOZ_options
import builder_func

def chunks(seq, n):
    return (seq[i:i+n] for i in range(0, len(seq), n))

def dict_chunks(seq, n):
    if len(seq) == 0:
        out = iter([])
    else:
        keys, vals = izip(*seq.iteritems())
        out = (
            dict((keys[ii], vals[ii]) for ii in xrange(i, i + n)
                 if ii < len(seq))
            for i in xrange(0, len(seq), n)
        )
    return(out)

class_cpt = Value('i', -1)
file_cpt = Value('i', -1)

class SIXMOZ_builder():
    rlock = Manager().RLock()
    def __init__(self, files, idl_files):
        self.classes = {}
        self.files = files
        self.idl_files = idl_files
        CppHeaderParser.ignoreSymbols += SIXMOZ_rules.to_ignore

    def init(self):
        self.parse_header_files()
        return (self.classes)

    def run(self):
        SIXMOZ_logger.print_info("Stage */6: Managing Typedef's")
        local_classes = {}
        chunk_size = 50
        if (chunk_size > len(self.classes)):
            chunk_size = int(len(self.classes) / SIXMOZ_options.workers)
        listes = list(dict_chunks(self.classes, int(len(self.classes) / chunk_size)))
        with concurrent.futures.ProcessPoolExecutor(max_workers=SIXMOZ_options.workers) as executor:
            future_task = {executor.submit(manage_typedefs, self.classes, liste): liste for liste in listes}
            for future in concurrent.futures.as_completed(future_task):
                try:
                    local_classes.update(future.result())
                except Exception as exc:
                    print('Worker generated an exception: %s' % (exc))
                    continue
        self.classes = local_classes
        print("")
        self.writer = SIXMOZ_writer(self.classes)
        self.add_full_heritage()
        self.find_override()
        self.writer.run()

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
                else:
                    SIXMOZ_logger.print_debug("Inherit Error: " + self.classes[classname]['inherits'][j] + " not found for " + classname)

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
                                SIXMOZ_logger.print_debug("Class: " + classname + " inherits " + simple_inherits)
                                add.add(hidden_inherits)
                                change = 1
                            else:
                                SIXMOZ_logger.print_debug("OTHER: " + classname + " inherits " + simple_inherits)
                        self.classes[classname]['inherits'] = list(add)

    def parse_header_files(self):
        SIXMOZ_logger.print_info("Stage 2/6: Parsing Header Files")
        nb_files = len(self.files) + len(self.idl_files)
        files = self.files + self.idl_files
        self.classes = {}
        saveout = sys.stdout
        chunk_size = 50
        if (chunk_size > len(files)):
            chunk_size = int(len(files) / SIXMOZ_options.workers)
        listes = list(chunks(files, int(len(files) / chunk_size)))
        #with RLock more than 2 workers looses time...
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
#        with concurrent.futures.ProcessPoolExecutor(max_workers=SIXMOZ_options.workers) as executor:
            future_task = {executor.submit(do_parse, liste, len(files)): liste for liste in listes}
            for future in concurrent.futures.as_completed(future_task):
                try:
                    self.classes.update(future.result())
                except Exception as exc:
                    sys.stdout = saveout
                    print('Worker generated an exception: %s' % (exc))
                    continue
        sys.stdout = saveout

def manage_typedefs(all_classes, liste):
    global class_cpt

    for classname in all_classes:
        for name in all_classes[classname]['typedefs']:
            for nclassname in liste:
                for inh in liste[nclassname]['inherits']:
                    if inh == name and all_classes[classname]['typedefs'][name] not in all_classes[nclassname]['inherits']:
                        liste[nclassname]['inherits'].append(all_classes[classname]['typedefs'][name])
                        SIXMOZ_logger.print_debug(classname + " typedef inherits: " + all_classes[classname]['typedefs'][name])
                        break
    class_cpt.value += len(liste)
    SIXMOZ_logger.foo_print("[" + str(class_cpt.value * 100 / len(all_classes))  + " %]")
    return (liste)

def do_parse(files, nb_files):
    global file_cpt

    classes = {}
    accessType_tab = [ "public", "private", "protected" ]
    saveout = sys.stdout
    dev_null = open("/dev/null", 'w')
    for id_file in range(len(files)):
        try:
            file_cpt.value += 1
            sys.stdout = dev_null
            with SIXMOZ_builder.rlock:
                cppHeader = CppHeaderParser.CppHeader(files[id_file])
            sys.stdout = saveout
        except CppHeaderParser.CppParseError as e:
            sys.stdout = saveout
            SIXMOZ_logger.print_error(str(e), files[id_file])
            continue
        except Exception as e:
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
            if (classname in classes and sys.argv[1] in classes[classname]['filename']):
                SIXMOZ_logger.print_debug("Duplicate: " + files[id_file] + " => " + classname)
                continue
            classes[classname] = {}                
            classes[classname]['filename'] = files[id_file]
            classes[classname]['inherits'] = []
            classes[classname]['namespace'] = namespace
            classes[classname]['funcs'] = {}
            classes[classname]['meths'] = {}
            classes[classname]['Ofuncs'] = {}
            classes[classname]['Omeths'] = {}
            classes[classname]['nested_typedefs'] = {}
            classes[classname]['typedefs'] = {}
            for inherit in range(len(cppHeader.classes[HeaderClass]["inherits"])):
                classes[classname]['inherits'].append(cppHeader.classes[HeaderClass]["inherits"][inherit]["class"])
                SIXMOZ_logger.print_debug("Inherits: " +  classes[classname]['inherits'][inherit])
            for accessType in accessType_tab:
                for id_func in range(len(cppHeader.classes[HeaderClass]["methods"][accessType])):
                    SIXMOZ_logger.print_debug("meth name: " + cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"])
                    SIXMOZ_logger.print_debug("meth ret: " + cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"] \
                                    + " => " + builder_func.check_ret(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"]))
                    SIXMOZ_logger.print_debug(cppHeader.classes[HeaderClass]["methods"][accessType][id_func])
                    meths = builder_func.check_ret(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"])
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
                            classes[classname]['Omeths'][len(classes[classname]['Omeths'])] = builder_func.over_meth(meths), \
                                builder_func.over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                        SIXMOZ_logger.print_debug("Meths: " + meths)
                        classes[classname]['meths'][len(classes[classname]['meths'])] = builder_func.over_meth(meths), \
                            builder_func.over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                    else:
                        SIXMOZ_logger.print_debug("Funcs: " + meths)
                        classes[classname]['funcs'][len(classes[classname]['funcs'])] = builder_func.over_meth(meths), \
                            builder_func.over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                    SIXMOZ_logger.print_debug(classname + " Funcs(" + str(len(classes[classname]['funcs'])) + ") " + " meths(" + str(len(classes[classname]['meths'])) + ")")
            classes[classname]['nested_typedefs'] = cppHeader.classes[HeaderClass]._public_typedefs
            classes[classname]['typedefs'] = cppHeader.typedefs
            for name in cppHeader.classes[HeaderClass]._public_typedefs:
                SIXMOZ_logger.print_debug("standard: " + cppHeader.classes[HeaderClass]._public_typedefs[name] + " => " + name)
            for l in classes[classname]['funcs']:
                SIXMOZ_logger.print_debug("Func: " + str(l)+ " " + classname + "::" + classes[classname]['funcs'][l][0])
            for l in classes[classname]['meths']:
                SIXMOZ_logger.print_debug("Meth: " + str(l)+ " " + classname + "::" + classes[classname]['meths'][l][0])
            for name in cppHeader.typedefs:
                SIXMOZ_logger.print_debug("OTHER: " + cppHeader.typedefs[name] + " => " + name) 
    SIXMOZ_logger.foo_print("[" + str(file_cpt.value * 100 / nb_files)  + " %]")
    dev_null.close()
    return (classes)
