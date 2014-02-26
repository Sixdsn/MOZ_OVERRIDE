#!/usr/bin/python

import sys

sys.path[0:0] = [ "modules" ]

from override import SIXMOZ_override

Six = SIXMOZ_override()
Six.run()
