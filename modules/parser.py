#!/usr/bin/python

import sys
import CppHeaderParser

from logger import SIXMOZ_logger
from rules import SIXMOZ_rules
from stats import SIXMOZ_stats
from options import SIXMOZ_options
from files import SIXMOZ_files

def manage_typedefs(classes):
    SIXMOZ_logger.print_info("Stage */6: Managing Typedef's")
    for classname in classes:
        for name in classes[classname]['typedefs']:
            for nclassname in classes:
                for inh in classes[nclassname]['inherits']:
                    if inh == name and classes[classname]['typedefs'][name] not in classes[nclassname]['inherits']:
                        classes[nclassname]['inherits'].append(classes[classname]['typedefs'][name])
                        SIXMOZ_logger.print_debug(classname + " typedef inherits: " + classes[classname]['typedefs'][name])

def fuck_meth(line, endlit, pareit):
    while (endlit > pareit + 1 and not line[endlit].isalpha()):
        endlit = endlit - 1
    if line[endlit].isalpha():
        endlit = endlit + 1
    return (endlit)

## @brief determine the good position to add MOZ_OVERRIDE
## @param line string
#  it int
## @returns position
def get_good_pos(line, it):
    l = line.find('{', it)
    m = -1
    n = -1
    if (l != -1):
        n = line.rfind(')', it, l)
        if (n != -1):
            m = fuck_meth(line, l, n)
            #m = line.rfind('\n', n, l)
        else:
            m = line.rfind('\n', it, l)
    if (m != -1 and m < l):
        l = m
    if (l == -1):
        l = line.find('= 0;', it)
        if (l == -1):
            l = line.find(';', it);
    if (l == -1):
        l = len(line);
    return (l)

## @brief add $to_add at the good position 
#  on the complete method declaration line
## @param line string
## @returns the line modified and added = 1 if line is modified
def add_it(line, it):
    
    SIXMOZ_logger.print_debug("Error: " + line)
    added = 0
    l = get_good_pos(line, it)
    mod = line[:l]
    if ((len(line[:l]) - 1) >= 0 and line[:l][len(line[:l]) - 1] != ' '):
        mod += " "
    mod += SIXMOZ_rules.to_add
    if (len(line[l:]) > 0 and line[l:][0] != ';' and line[l:][0] != ' ' and line[l:][0] != '\n'):
        mod += " "
    mod += line[l:]
    SIXMOZ_stats.modified_meths += 1
    added = 1
    return (mod, added)

## @brief get the full meth declaration content
#  in case the declaration is on multiples lines
## @param liste current line
#  i line counter in file
#  content file modified
## @returns found: = 1 if $to_add added
def find_meth(liste, i, content):
    ok = 1
    found = 0
    while (ok == 1):
        mod = ""
        while (i < len(liste) and mod.find(';') == -1 and mod.find('{') == -1):
            mod += liste[i]
            i += 1
        if (mod.find(';') != -1 or mod.find('{') != -1):
            if (mod.find(SIXMOZ_rules.to_add) == -1):
                mod, found = add_it(mod, 0)
            ok = 0
            content += mod
            mod = ""
        else:
            content += mod
        if (i >= len(liste)):
            ok = 0
    return (i, mod, content, found)

# def void_write_file(filename, content = 0):
#     SIXMOZ_logger.print_verbose("[DRYRUN]: " + filename)

## @brief open each needed file to modify it
## @param filename string
#  classname string 
#  line current line
## @returns
def modify_file(filename, classname, line, orig):
    if (SIXMOZ_options.path not in filename):
        return
    if (filename not in SIXMOZ_files.get_files()):
        return
    if orig.find(SIXMOZ_rules.to_add) != -1 or orig.find(SIXMOZ_rules.to_find) != -1:
        SIXMOZ_stats.overrided.append(classname + "::" + orig)
        return
    liste = file(filename, "r").readlines()
    i = 0
    content = ""
    modified = 0
    while i < len(liste):
        mod =  ""
        mod = liste[i]
        if ((i + 1) == line):
            SIXMOZ_logger.print_debug("Before: [" + str(line) + "] " + str(liste[i]))
            if (liste[i].find(SIXMOZ_rules.to_add) == -1):
                i, mod, content, found = find_meth(liste, i, content)
                if (found == 1):
                    SIXMOZ_stats.overrided.append(classname + "::" + orig)
                    SIXMOZ_stats.real_overrided.append(classname + "::" + orig)
                    modified = 1
                    if (filename not in SIXMOZ_stats.mod_files):
                        SIXMOZ_stats.mod_files.append(filename)
            else:
                content += mod
                i += 1
        elif (len(mod) != 0):
            content += mod
            i += 1
        else:
            content += liste[i]
            i += 1
    if (modified == 1):
        SIXMOZ_logger.dryrun(filename, content)

## @brief adds the #include "Attributes.h"
#  to every file were its not included
#  and where $to_add has been added
## @param void
## @returns void
def add_attributes():
    SIXMOZ_logger.print_info("Stage 6/6: Adding Attributes.h")
    for filename in SIXMOZ_stats.mod_files:
        if (filename[-4:] != ".cpp"):
            liste = file(filename, "r").readlines()
            first = 0
            for li in liste:
                if (li.find("Attributes.h") != -1 and li.find("#include ") != -1):
                    first = 1
            content = ""
            if (first == 0):
                for li in liste:
                    if (li.find("#include") != -1 and first == 0):
                        content += '#include "mozilla/Attributes.h"\n'
                        first = 1
                    content += li
                SIXMOZ_logger.dryrun(filename, content)
            
## @brief a sanity check that adds a preprocess test
#  at EOF (not used by default)
## @param void
## @returns void
def sanity_check():
    for filename in SIXMOZ_stats.mod_files:
        liste = file(filename, "r").readlines()
        content = ""
        for li in liste:
            content += li
        content += '\n#if !defined(MOZ_HAVE_CXX11_OVERRIDE)\n \
#warning "MOZ_OVERRIDE Undefined"\n \
#endif\n'
        fd = file(filename, "w")
        fd.write(content)
        fd.close()

## @brief del $to_find from existing meth
#  to check the signature with other meths
## @param meth method to find
## @returns meth string without $to_find
def over_meth(meth):
    meth = meth.replace("NS_IMETHOD_ ", "")
    meth = meth.replace("NS_IMETHOD ", "")
    meth = meth.replace("virtual ", "")
    meth = meth.replace(SIXMOZ_rules.to_add, "")
    meth = meth.replace(SIXMOZ_rules.to_find, "")
    meth = meth.replace("  ", " ")
    return (meth)

## @brief check for duplicate first value over_meth(meth) in meths/funcs dict
## @param zobdict meths/funs dict
#  zob value to check
## @returns 1 if value is already in 0 if we must add it
def is_in(zobdict, zob):
    for l in zobdict:
        if zobdict[l][0] == zob:
            return 1
    return 0

def add_moz_override(classes):
    SIXMOZ_logger.print_info("Stage 5/6: Adding " + SIXMOZ_rules.to_add + " to files")
    for classname in classes:
        for k in classes[classname]['Omeths']:
            modify_file(classes[classname]['filename'], classname, classes[classname]['Omeths'][k][3], classes[classname]['Omeths'][k][2])
        for k in classes[classname]['Ofuncs']:        
            modify_file(classes[classname]['filename'], classname, classes[classname]['Ofuncs'][k][3], classes[classname]['Ofuncs'][k][2])

## @brief creates the heritage tree for all methods
## @param classes dict of all classes
#  classname string
## @returns void
def find_override(classes, files):
    SIXMOZ_logger.print_info("Stage 4/6: Finding methods to override")
    for classname in classes:
        for j in range(len(classes[classname]['inherits'])):
            if (classes[classname]['inherits'][j] in classes):
                SIXMOZ_logger.print_debug(classname + " inherits " + classes[classname]['inherits'][j])
                for m in classes[classes[classname]['inherits'][j]]['meths']:
                    SIXMOZ_logger.print_debug("1: " + classes[classname]['inherits'][j] + "::" + classes[classes[classname]['inherits'][j]]['meths'][m][0])
                    for l in classes[classname]['funcs']:
                        SIXMOZ_logger.print_debug("2: " + classes[classname]['inherits'][j] + "::" + classes[classes[classname]['inherits'][j]]['meths'][m][0] \
                                        + " " + classname + "::" + classes[classname]['funcs'][l][0])
                        if classes[classes[classname]['inherits'][j]]['meths'][m][0] == classes[classname]['funcs'][l][0]:
                            classes[classname]['Ofuncs'][len(classes[classname]['Ofuncs'])] = classes[classname]['funcs'][l]
                            SIXMOZ_logger.print_debug("OVERRIDE2: " + classes[classname]['inherits'][j] + "::" + classes[classes[classname]['inherits'][j]]['meths'][m][2] \
                                            + " and " + classname + "::" + classes[classname]['funcs'][l][2])
                    for l in classes[classname]['meths']:
                        SIXMOZ_logger.print_debug("3: " + classes[classname]['inherits'][j] + "::" + classes[classes[classname]['inherits'][j]]['meths'][m][0] \
                                        + " " + classname + "::" + classes[classname]['meths'][l][0])
                        if classes[classes[classname]['inherits'][j]]['meths'][m][0] == classes[classname]['meths'][l][0]:
                            classes[classname]['Omeths'][len(classes[classname]['Omeths'])] = classes[classname]['meths'][l]
                            SIXMOZ_logger.print_debug("OVERRIDE3: " + classes[classname]['inherits'][j] + "::" + classes[classes[classname]['inherits'][j]]['meths'][m][2] \
                                            + " line [" + str(classes[classes[classname]['inherits'][j]]['meths'][m][3]) + "]" \
                                            + " and " + classname + "::" + classes[classname]['meths'][l][2] + " line [" + str(classes[classname]['meths'][l][3]) + "]")

def add_full_heritage(classes):
    SIXMOZ_logger.print_info("Stage 3/6: Creating Heritage Tree")
    add_heritage_it(classes)

def add_heritage_it(classes):
    change = 1
    while (change == 1):
        change = 0
        for classname in classes:
            add = set(classes[classname]['inherits'])
            for simple_inherits in classes[classname]['inherits']:
                if (str(classes[classname]['namespace'] + simple_inherits) in classes and simple_inherits not in classes):
                    simple_inherits = str(classes[classname]['namespace'] + simple_inherits)
                if (simple_inherits in classes):
                    for hidden_inherits in classes[simple_inherits]['inherits']:
                        if (hidden_inherits in classes and hidden_inherits not in classes[classname]['inherits'] and hidden_inherits != classname):
                            add.add(hidden_inherits)
                            change = 1
                        else:
                            SIXMOZ_logger.print_debug("OTHER: " + classname + " inherits " + simple_inherits)
                    classes[classname]['inherits'] = list(add)

def is_macro(bar):
    par = 0
    for i in range(len(bar)):
        if (not bar[i].isupper() and not bar[i] == '_' and not bar[i] == '(' and not bar[i] == ')' and not bar == ":"):
            return False
    return True

def check_ret_namespace(bar):
    res = ""
    start = bar.rfind("::")
    if (start == -1):
        return (bar)
    end = bar.rfind(" ", 0, start)
    if (end == -1):
        res = ""
    res = bar[:end + 1]
    res += bar[start + 2:]
    SIXMOZ_logger.print_debug("Ret: " + bar + " => " + res)
    return (res)

def check_ret(bar):
    if (bar.find("NS_IMETHOD") == 0):
        return check_ret_namespace(bar)
    words = bar.split(' ')
    j = 0
    for i in range(len(words)):
        if is_macro(words[i]) == False:
            res = " ".join(words[i:])
            if (res == "*" or res == "&"):
                return check_ret_namespace(bar)
            return check_ret_namespace(res)
        else:
            j = j + 1
    if i == j - 1:
        return ""
    return check_ret_namespace(bar)

def parse_header_files(mod_files, idl_files):
    SIXMOZ_logger.print_info("Stage 2/6: Parsing Header Files")
    nb_files = len(mod_files) + len(idl_files)
    accessType_tab = [ "public", "private", "protected" ]
    saveout = sys.stdout
    CppHeaderParser.ignoreSymbols += SIXMOZ_rules.to_ignore
    classes = {}
    dev_null = open("/dev/null", 'w')
    files = mod_files + idl_files
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
                                    + " => " + check_ret(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"]))
                    SIXMOZ_logger.print_debug(cppHeader.classes[HeaderClass]["methods"][accessType][id_func])
                    meths = check_ret(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["rtnType"])
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
                            classes[classname]['Omeths'][len(classes[classname]['Omeths'])] = over_meth(meths), \
                                over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                                cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                        SIXMOZ_logger.print_debug("Meths: " + meths)
                        classes[classname]['meths'][len(classes[classname]['meths'])] = over_meth(meths), \
                            over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"], \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["line_number"], \
                            cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["name"]
                    else:
                        SIXMOZ_logger.print_debug("Funcs: " + meths)
                        classes[classname]['funcs'][len(classes[classname]['funcs'])] = over_meth(meths), \
                            over_meth(cppHeader.classes[HeaderClass]["methods"][accessType][id_func]["debug"]), \
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
        del cppHeader
    print ""
    dev_null.close()
    return (classes)
