#!/usr/bin/python

import sys

sys.path[0:0] = [ "modules" ]

from rules import SIXMOZ_rules

SIXMOZ_rules.init()

from override import SIXMOZ_override

Six = SIXMOZ_override()
Six.run()
