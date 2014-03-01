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
            funcs = [ files.get_files, files.get_idl_files ]
            future_task = {executor.submit(func): func for func in funcs}
            for future in concurrent.futures.as_completed(future_task):
                if (future_task.keys().index(future) == 1):
                    self.files = future.result()
                elif (future_task.keys().index(future) == 0):
                    self.idl_files = future.result()
        self.builder = SIXMOZ_builder(self.files, self.idl_files)

    def run(self):
        self.classes = self.builder.init()
        self.stats.display_base(self.classes, self.files, self.idl_files)
        self.builder.run()
        self.stats.display(self.classes, self.files, self.idl_files)
