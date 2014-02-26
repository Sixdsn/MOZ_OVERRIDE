#!/usr/bin/python

from logger import SIXMOZ_logger
from rules import SIXMOZ_rules
from stats import SIXMOZ_stats
from options import SIXMOZ_options
from files import SIXMOZ_files

class SIXMOZ_writer():
    def __init__(self, classes):
        self.classes = classes

    def run(self):
        self.add_moz_override()
        add_attributes()

    def add_moz_override(self):
        SIXMOZ_logger.print_info("Stage 5/6: Adding " + SIXMOZ_rules.to_add + " to files")
        for classname in self.classes:
            for k in self.classes[classname]['Omeths']:
                modify_file(self.classes[classname]['filename'], classname, self.classes[classname]['Omeths'][k][3], self.classes[classname]['Omeths'][k][2])
            for k in self.classes[classname]['Ofuncs']:
                modify_file(self.classes[classname]['filename'], classname, self.classes[classname]['Ofuncs'][k][3], self.classes[classname]['Ofuncs'][k][2])

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

## @brief open each needed file to modify it
## @param filename string
#  classname string 
#  line current line
## @returns
def modify_file(filename, classname, line, orig):
    if (SIXMOZ_options.path not in filename or filename not in SIXMOZ_files.get_files()):
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
