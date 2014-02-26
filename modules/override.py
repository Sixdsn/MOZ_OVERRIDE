#!/usr/bin/python

from files import SIXMOZ_files
from stats import SIXMOZ_stats
from options import SIXMOZ_options
import parser

class SIXMOZ_override():
    def __init__(self):
        self.stats = SIXMOZ_stats()
        self.files = SIXMOZ_files.get_files()
        self.idl_files = SIXMOZ_files.get_idl_files()
        self.classes = parser.parse_header_files(self.files, self.idl_files)

    def run(self):
        self.stats.display_base(self.classes, self.files, self.idl_files)
        parser.manage_typedefs(self.classes)
        parser.add_full_heritage(self.classes)
        parser.find_override(self.classes, self.files)
        parser.add_moz_override(self.classes)
        parser.add_attributes()
        self.stats.display(self.classes, self.files, self.idl_files)
