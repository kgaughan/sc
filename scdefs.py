# Geoff's Sound Change Applier version 0.5 (March 2009)
# First created by Geoff Eddy, from an idea by Mark Rosenfelder
# You may obtain this from http://www.cix.co.uk/~morven/lang/sc.html
#
# You may use this program for any purpose provided that you credit
# the author(s) appropriately, do not restrict what others can do with
# it, and do not sell it or allow it to be sold.

##############################################################################

# This file contains common definitions.

import sys

# Exceptions and how to call them.

class scException(Exception):
    def __init__(self, s, *args): self.s = s % args
    def __str__(self): return self.s

def die(n, s, *args):
    t = s % args
    raise scException("Error at line number %s:\n%s\n", n, t)

def warn(n, s, *args):
    t = s % args
    sys.stderr.write("Warning at line %d: %s:\n" % (n, t))

# Functions to print in colour, if you have an ANSI-compatible terminal.

def cols(s, n, b = True):
    if not b: return s
    return ("\033[1;%dm" % n) + s + "\033[0m"

def colourcat(s):
    t = ""

    for c in s:
        if c in "<>[]|#%+*?$`": t += cols(c, 33)
        else:       t += c

    return t

##############################################################################
