#!/usr/bin/python

import concurrent.futures

from stats import SIXMOZ_stats
from builder import SIXMOZ_builder
import files

class SIXMOZ_override():
    def __init__(self):
        self.classes = []
        self.stats = SIXMOZ_stats()
        with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
            future_files = executor.submit(files.get_files)
            future_idl_files = executor.submit(files.get_idl_files)
            self.files = future_files.result()
            self.idl_files = future_idl_files.result()
        self.builder = SIXMOZ_builder(self.files, self.idl_files)

    def run(self):
        self.classes = self.builder.init()
        self.stats.display_base(self.classes, self.files, self.idl_files)
        self.builder.run()
        self.stats.display(self.classes, self.files, self.idl_files)
