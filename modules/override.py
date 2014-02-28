#!/usr/bin/python

from files import SIXMOZ_files
from stats import SIXMOZ_stats
from parser import SIXMOZ_parser

class SIXMOZ_override():
    def __init__(self):
        self.classes = []
        self.stats = SIXMOZ_stats()
        self.files = SIXMOZ_files.get_files()
        self.idl_files = SIXMOZ_files.get_idl_files()
        self.parser = SIXMOZ_parser(self.files, self.idl_files)

    def run(self):
        self.classes = self.parser.init()
        self.stats.display_base(self.classes, self.files, self.idl_files)
        self.parser.run()
        self.stats.display(self.classes, self.files, self.idl_files)
