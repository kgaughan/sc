# This file is part of Geoff's Sound Change Applier, version 0.8
# (August 2010). You can obtain the latest version of this program
# from http://gesc19764.pwp.blueyonder.co.uk/sca.html

""" This file defines the types of item which SCA uses for matching."""

import re, random

from SCAdefs import *

##############################################################################

""" The base class of all items; not used by itself. Inherited methods
in subclasses are in general commented here only.

Subclasses must override compileText(), compileRE(), and
convert(). indexable() and validate() may also need overridden.
"""

class SCAItem:
    """ Construct this item.
    name: the type of the item; used only in debugging
    p:    the parent (SCARulePart) of which this item is a part
    n:    the position of the item in BEFORE
    s:    the text from which the item is constructed
    esc:  True if special characters shuold be escaped
    """
    def __init__(self, name, p, n, s = None, esc = True):
        self.name, self.parent, self.index, self.esc = name, p, n, esc

        # This is meaningful only in categories and lists. It stores
        # their values.
        self.values   = []

        # This is 0 for PRE, 1 for BEFORE, and 2 for POST. It's only
        # meaningful where the part contains "<", "%", or ">".
        self.group   = None

        # This gets converted to '\' + self.group in the above
        # situation. It's needed because a regexp like "(\1)" can't
        # be compiled in isolation.
        self.extrexp = None

        # This is like self.group, but applicable to maps only.
        self.part    = None

        # When referring to a specific item in BEFORE, this stores its
        # index.
        self.ref     = None

        # True only for lists and categories which have random lookup.
        self.random  = False

        # This contains the text which the item displays to the user.
        self.text = self.compileText(s)

        # This contains the regexp which the item uses for
        # matching. It should be None if the item appears only in
        # AFTER, e.g. references and maps.
        self.rexp = self.compileRE(s)

        if self.rexp is None:
            self.re = None
        else:
            try:
                self.re = re.compile(self.rexp)
            except:
                raise SCAException("Bad resulting regexp '%s'; " +
                                   "this is a bug", self.rexp)

    """ Convert a string from AFTER according to this item.
    R: the item in BEFORE to which it applies
    s: the string to convert
    groups: matched groups in main rexp (PRE, BEFORE, POST)
    m: matched groups in BEFORE
    """
    def convert(self, R, s, *args): return s

    """ How should this item be displayed to the user as a string? """
    def getText(self): return self.text

    """ How should this item be displayed to the user as a regexp? """
    def getRexp(self):
        if self.rexp: return self.rexp
        return ""

    """ Return the external regexp if we have one, otherwise the
    normal regexp. This is used when building the regexp for the
    entire rule, when we can use '\1'.
    """
    def getExtRexp(self):
        if self.extrexp: return self.extrexp
        return self.getRexp()

    """ How many sub-items are in this item?
    This is only meaningful for lists and categories.
    """
    def __len__(self): return len(self.values)

    """ Can we look up values? Meaningful for categories and lists. """
    def indexable(self): return False

    """ Generate a reasonable representation of this item. """
    def __repr__(self):
        f = "%s %s [text = '%s', rexp = '%s', ref = %s, " +\
            "group = %s, part = %s]"

        return f % (self.index, self.name, self.text, self.rexp,
                self.ref, self.group, self.part)

    """ Which item in BEFORE does this item refer to? By default, the
    one with the same index.
    """
    def getRef(self):
        if self.ref is not None: return self.ref
        return self.index + 1

    """ Does this item refer to a valid item in BEFORE? This traps
    unworkable changes like 'a <cat>' and 'foo 2'.
    """
    def validateRef(self, p, ref, checkLen, verbose):
        if p is None: p = 1
        
        s    = ["PRE", "BEFORE", "POST"][p]
        part = self.parent.getPart(p)
        n    = len(part)

        if ref > n or ref + n < 0:
            raise SCAException("'%s' in AFTER refers to nonexistent item "
                               + "(%d of %d) in %s",
                               self.text, self.ref, n, s)

        I = part[ref]
        if self.random: return

        # FIXME: this is risky
        if self.name == 'map' and I.name == 'zero': return

        if not I.indexable():
            raise SCAException("Item %d '%s' in AFTER does not refer to " +
                               "a category or a list in %s",
                               ref, self.text, s)

    """ Ensure that this item is valid; raise an exception of not. """
    def validate(self, verbose): pass

##############################################################################

""" Literals which need no further conversion; typically strings,
perhaps with quantifiers.
"""

class SCALiteral(SCAItem):
    def __init__(self, *args): SCAItem.__init__(self, "literal", *args)
    def compileText(self, s): return s
    def compileRE(  self, s): return s
    def convert(self, *args):  return self.text

##############################################################################

""" Zero. Very boring. """

class SCAZero(SCAItem):
    def __init__(self, *args): SCAItem.__init__(self, "zero", *args)
    def compileText(self, s): return "0"
    def compileRE(  self, s): return ""
    def convert(self, *args):  return ""

##############################################################################

""" Strings as referred to with '$foo$'. """

class SCAString(SCAItem):
    def __init__(self, quants, *args):
        SCAItem.__init__(self, "string", *args)

    """ We refer to strings with their names, not their values. """
    def compileText(self, s): return "$" + s + "$"

    """ But the regexp needs the value, which must exist and may need
    to be escaped.
    """
    def compileRE(  self, s):
        t = self.parent.sca.getDef("string", s)

        if t is None: raise SCAException("Unknown string '%s'", s)

        if self.esc: return t

        ret = ""

        for c in t:
            if c in '|[]{}+?*.^$': ret += '\\'
            ret += c

        return ret

    """ Strings convert to their values. """
    def convert(self, *args): return self.re.pattern

##############################################################################

""" Part references, i.e. '%'. '<', and '>'.
"""

class SCAPartref(SCAItem):
    def __init__(self, *args):
        SCAItem.__init__(self, "group", *args)
        self.group = int(self.text)

    def compileText(self, s): return s

    def indexable(self): return True

    """ Part references don't compile directly. """
    def compileRE(self, s):
        self.extrexp = "\\" + self.text
        return None

##############################################################################

""" Base class for categories and lists, and anything else which can
be looked up like an array.
"""

class SCAVector(SCAItem):
    """ We may have quantifiers, for example '<cat>*', which need to
    be taken into account.
    """
    def __init__(self, name, quants, *args):
        self.quants = quants
        SCAItem.__init__(self, name, *args)
        if self.ref is None: self.ref = self.index + 1

    """ Construct a string from the individual values, with
    delimiters.
    """
    def makeList(self, L, s1, s2, sep): return s1 + sep.join(L) + s2

    def compileText(self, s):
        # This is a convenient place to work out what the item
        # actually represents.
        self.expand(s)
        return self.makeList([s], *self.getTextDelims()) + self.quants

    def compileRE(self, s):
        return self.makeList(self.values, *self.getRexpDelims()) + self.quants

    def convert(self, R, s, *args):
        if self.random: n = random.randrange(len(self))
        else: n = R[self.ref].find(s)

        if n >= len(self): return ""
        ret = self.values[n]
        if ret == '0': ret = ''
        return ret

    """ Retrieve the index of _s_. For example, finding 'c' in '<abc>'
    returns 2.
    """
    def find(self, s): return self.values.index(s)

    def indexable(self): return True

    def validate(self, verbose):
        self.validateRef(1, self.ref, True, verbose)

##############################################################################

""" Categories, i.e. SCAVectors of symbols: <abc>, <+def>, and so on. """

class SCACategory(SCAVector):
    def __init__(self, *args):
        SCAVector.__init__(self, "cat", *args)

    def getTextDelims(self): return "<", ">", ""

    def getRexpDelims(self): return "[", "]", ""

    def expand(self, s):
        try:
            t, i = stripInt(s)
            if i is not None: self.ref = i
            s = t
        except ValueError:
            pass

        if s[0] == '@': self.random, s = True, s[1:]

        self.values = self.parent.sca.getCat(s)

        if self.values is None:
            raise SCAException("Cannot evaluate category '%s'", s)

##############################################################################

class SCAFeature(SCAVector):
    def __init__(self, *args):
        SCAVector.__init__(self, "feature", *args)

    def getTextDelims(self): return "[", "]", ","

    def getRexpDelims(self): return "[", "]", ""

    def expand(self, s):
        L = s.split(",")
        if len(L) == 0: raise SCAException("Empty feature reference")

        ret = self.getFeature(L.pop(0))

        for t in L:
            ret = "".join([c for c in ret if c in self.getFeature(t)])

        self.values = ret

    def getFeature(self, s):
        if s[0] not in "-+":
            raise SCAException("Bad feature reference '%s'", s)

        T = self.parent.sca.getDef("feature", s[1:])

        if T is None:
            raise SCAException("Unknown feature '%s'", s)

        return T["-+".index(s[0])]

##############################################################################

""" Lists, i.e. SCAVectors of strings: [foo,bar,baz]. """

class SCAList(SCAVector):
    def __init__(self, *args):
        SCAVector.__init__(self, "list", *args)

    def getTextDelims(self): return "[",   "]", ","

    # need the "?:" to stop the parentheses being interpreted as
    # groups
    def getRexpDelims(self): return "(?:", ")", "|"

    def expand(self, s):
        if s[0] == '@': self.random, s = True, s[1:]

        d = self.parent.sca.getDef('list', s)

        if d is not None:
            self.values = d
            return

        for t in s.split(','):
            if t[0] == '$':
                self.values.append(self.parent.sca.findDef('string', t[1:]))
            else:
                self.values.append(t)

    def getExtRexp(self):
        if self.extrexp: return self.extrexp
        return self.getRexp()

##############################################################################

""" Indexes into BEFORE, which are represented by numbers. """

class SCAIndex(SCAItem):
    def __init__(self, *args):
        SCAItem.__init__(self, "index", *args)
        self.ref = int(self.text)

    def compileText(self, s): return s

    def compileRE(self, s): return None

    def indexable(self): return True

    def validate(self, verbose):
        self.validateRef(1, self.ref, False, verbose)

##############################################################################

""" Blends. """

blendre = re.compile("^([<>]?)(-?\d?)$")

class SCABlend(SCAItem):
    def __init__(self, q, p, n, s, esc):
        SCAItem.__init__(self, "blend", p, n, s, esc)

        if len(s) == 0: raise SCAException("Nothing given in blend")

        if ":" not in s:
            raise SCAException("No colon in blend '%s'", s)

        L = s.split(":")

        if len(L) > 2:
            raise SCAException("Too many colons in blend '%s'", s)

        self.catpart, self.catindex, self.cat = self.parse(L[0], "cat")
        self.pospart, self.posindex, self.pos = self.parse(L[1], "index")

    """ Work out the part and index from half of a blend. """
    def parse(self, s, t):
        m, c = blendre.match(s), s

        if m is None:
            if not self.parent.sca.hasDef("cat", c):
                raise SCAException("Unknown category '%s' in blend", c)

            part, index = 1, self.index + 1
        else:
            p, i = m.groups()

            if len(i) == 0: index = self.index + 1
            else:           index = int(i)

            if   p == "<": part = 0
            elif p == ">": part = 2
            else:          part = 1

            c = self.parent.getItem(part, index)

            if c is None or c[0] != "<" or c[-1] != ">":
                raise SCAException("'%s' is not a category", c)

            c = c[1:-1]

        if index > 0: index -= 1

        return part, index, self.parent.sca.getDef("cat", c)

    def compileText(self, s): return "{" + s + "}"
    def compileRE(self, s): return None

    def convert(self, R, s, groups, m):
        if self.pospart == 1:
            c = m[self.posindex]
        else:
            c = groups[self.pospart][self.posindex]

        return self.cat[self.pos.find(c)]
        
    def indexable(self): return True

    def validate(self, verbose): pass
#        self.validateRef(self.part, self.ref, True, verbose)

#        if self.afterref is not None:
#            self.validateRef(self.afterpart, self.afterref, True, verbose)

##############################################################################

""" A class to store exceptions - not the system type, but words which
should not be processed by specific rules.
"""
class SCAExceptionWords:
    def __init__(self): self.H = {}

    """ Add an exception.
    _name_: the name of the rule. This is not easily checked; if there
    is no rule with this name, the exception will be ignored.
    _words_: the words to which the exception will apply
    _dialects_: the dialects; None for all
    """
    def add(self, name, words, dialects = None):
        if name not in self.H: self.H[name] = []
            
        self.H[name].append((dialects, words))

    """ Read some exceptions from _filename_. We expect one of more of:
    @RULE dialects
    words
    more words
    """
    def readFromFile(self, filename, enc):
        f = codecs.open(filename, "r", enc)

        if f is None:
            raise SCAException("Exception file '%s' not found", filename)

        lastname, lastdial = None, None

        for line in f.readlines():
            line = line[:-1]

            if len(line) == 0 or line[0] == '#': continue

            if line[0] == '@':
                L = line[1:].split()
                lastname = L.pop(0)
                lastdial = "".join(L)
                continue

            if lastname is None:
                f.close()
                raise SCAException("No previous rule specified in "+
                                   "exception file '%s'", filename)

            self.add(lastname, line.split(), lastdial)

        f.close()

    """ Is _w_ in dialect _d_ an exception for rule _name_? """
    def isException(self, name, w, d):
        if name not in self.H: return False

        for dial, L in self.H[self]:
            if w not in L: continue
            if dial is not None and d not in dial: continue
            return True

        return False

##############################################################################
