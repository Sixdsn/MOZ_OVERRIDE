#!/usr/bin/python

import sys

sys.path[0:0] = [ "modules" ]

from files import SIXMOZ_files
from stats import SIXMOZ_stats
from options import SIXMOZ_options
import parser

SixStats = SIXMOZ_stats()

all_classes = parser.parse_header_files(SIXMOZ_files.get_files(), SIXMOZ_files.get_idl_files())
SixStats.display_base(all_classes, SIXMOZ_files.get_files(), SIXMOZ_files.get_idl_files())
parser.manage_typedefs(all_classes)
parser.add_full_heritage(all_classes)
parser.find_override(all_classes, SIXMOZ_files.get_files())
parser.add_moz_override(all_classes)
parser.add_attributes()
SixStats.display(all_classes, SIXMOZ_files.get_files(), SIXMOZ_files.get_idl_files())
