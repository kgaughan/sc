# Geoff's Sound Change Applier version 0.5 (March 2009)
# First created by Geoff Eddy, from an idea by Mark Rosenfelder
# You may obtain this from http://www.cix.co.uk/~morven/lang/sc.html
#
# You may use this program for any purpose provided that you credit
# the author(s) appropriately, do not restrict what others can do with
# it, and do not sell it or allow it to be sold.

##############################################################################

# Slightly more convoluted string indexing, which treats "1" as the
# first character in the string.

def extract(s, t):
    n = int(s)

    if n < 0: m = len(t) - n
    else:     m = n - 1

    if m >= len(t): die("%s: index out of range", s)

    return t[m]

##############################################################################

# The three types of conversion allowed in AFTER.

# Base class; boring.

class Conversion:
    def __init__(self, s, p): self.s = ""
    def convert(self, before, pre, post): return self.s
    def rexp(self): return self.s

# A straightforward character conversion.

class Char(Conversion):
    def __init__(self, s, p):
        Conversion.__init__(self, s, p)
        self.s = s[0]

    def convert(self, before, pre, post):
        if self.s == ">": return post
        if self.s == "<": return pre
        if self.s == "%": return before
        return self.s

# #n and #-n

class Index(Conversion):
    def __init__(self, s, p):
        Conversion.__init__(self, s, p)
        s = s[1:]
        if s == "": self.die("%s: no index", s)

        if s[0] == '-': neg = "-"; s = s[1:]
        else:           neg = ""

        if s == "": self.die("%s: no index", s)

        c, s = s[0], s[1:]

        if c not in "123456789":
            raise scException("%s: index is not a number", s)

        self.n = int(neg + c)

    def convert(self, before, pre, post):
        return extract(self.n, before)

    def rexp(self):
        if self.n > 0: return "#%s" % (1 + self.n)
        return "#%s" % self.n

# Mappings

class Map(Conversion):
    def __init__(self, s, p = None):
        i = s.find("}")

        if i < 0: raise scException("%s: no matching }", s)

        self.before, old, new = s[1:i].split(":")
        self.s1 = p.cat2re(old)[1:-1]
        self.s2 = p.cat2re(new)[1:-1]

        if len(self.s1) != len(self.s2):
            raise scException("Categories '%s' and '%s' are different lengths",
                     old, new)

    def convert(self, before, pre, post):
        if   self.before == ">": c = post
        elif self.before == "<": c = pre
        elif self.before == "%": c = before
        else:                    c = extract(self.before, before)

        i = self.s1.find(c)
        if i < 0: return before
        if self.s2[i] == "0": return ""
        return self.s2[i]

    def convertCat(self, s, p): return p.convertCat(s)[1:-1]

    def rexp(self):
        b = self.before
        if b in "012345678": b = 1 + int(b)
            
        return "{%s:%s:%s}" % (b, self.s1, self.s2)

##############################################################################
