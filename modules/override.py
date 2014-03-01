#!/usr/bin/python

from files import SIXMOZ_files
from stats import SIXMOZ_stats
from builder import SIXMOZ_builder

class SIXMOZ_override():
    def __init__(self):
        self.classes = []
        self.stats = SIXMOZ_stats()
        self.files = SIXMOZ_files.get_files()
        self.idl_files = SIXMOZ_files.get_idl_files()
        self.builder = SIXMOZ_builder(self.files, self.idl_files)

    def run(self):
        self.classes = self.builder.init()
        self.stats.display_base(self.classes, self.files, self.idl_files)
        self.builder.run()
        self.stats.display(self.classes, self.files, self.idl_files)
