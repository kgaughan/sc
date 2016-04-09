# This file is part of Geoff's Sound Change Applier, version 0.8
# (August 2010). You can obtain the latest version of this program
# from http://gesc19764.pwp.blueyonder.co.uk/sca.html

""" Basic definitions for SCA; functions which are genearlly useful
and not tied to a specific class.
"""

import codecs

##############################################################################

""" A useful SCA_specific exception class. """

class SCAException(Exception):
    def __init__(self, s, *args):
        if len(args) == 0: self.s = s
        else:              self.s = s % args

    def __repr__(self): return self.s

""" Strip a leading minus sign and digit, if present, from a
string. This is taken to represent an index, so positive values are
decremented by 1. So:

'1foo'  returns 'foo', 0
'-1foo' returns 'foo', -1
'foo'   returns 'foo', None
"""

def stripInt(s):
    if len(s) == 0: return "", None
    
    t = ""

    if s[0] == '-':         t += s[0]; s = s[1:]
    if s[0] in '123456789': t += s[0]; s = s[1:]

    if t == '': return s, None

    return s, int(t)

""" Add an ANSI colour codes to a string so that it wil be printed in
colour.
s: the string
n: the number of the code to add; should be between 30 and 47
b: True to actually add the colours, False to leave the string alone
"""

def cols(s, n, b = True):
    if not b: return s
    return "\033[1;%dm%s\033[0m" % (n, s)

""" Read from a file and yield each line in turn with its number,
subject to the following:

- Empty lines and lines which start with '#' are ignored
- Spaces at each end are removed first of all
- Anything following END, or in between SKIP and NOSKIP, will be
  ignored
- Anything after a non-initial '!' will be thrown away
- Backslashes can be used to join lines together
"""

def readfile(file, enc = "utf-8"):
    f = codecs.open(file, "r", enc)

    s, n = "", 0

    for line in f.readlines():
        n += 1
        if len(line) == 0 or line[0] == '#': continue
        if line[-1] == '\n': line = line[:-1]
        if len(line) == 0: continue

        line = line.strip()

        if "!" in line:
            i = line.index("!")
            if i > 0 and line[i - 1] != '\\': line = line[:i]

        if line[-1] == '\\': s += line[:-1]; continue

        yield s + line, n

        s = ""

""" Split a string, but treat escaped delimiters as text, not
delimiters. There may be a better way to so this with regexps, but
this will have to do for now.
"""

def escapedSplit(s, delim = None, n = None, esc = '\\'):
    if delim is None: sep = ' '
    else:             sep = delim

    if n is None: L = s.split(delim)
    else:         L = s.split(delim, n)

    a = []

    for t in L:
        if len(a) > 0 and a[-1][-1] == esc:
            a[-1] = a[-1][:-1] + sep + t
        else:
            a.append(t)

    return a

""" Parse a comma-separated list of ranges and return a list of the
numbers it represents. So:
'1,2,3' -> 1, 2, 3
'1-3,6' -> 1, 2, 3, 6
"""

def makeNumList(arg, delim1 = ',', delim2 = '-'):
    L = []
    
    for s in arg.split(","):
        if '-' not in s:
            L.append(int(s))
            continue

        n1, n2 = s.split("-")
        for n in range(int(n1), int(n2) + 1):
            if n not in L: L.append(n)

    return L

##############################################################################
