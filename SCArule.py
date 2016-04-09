# This file is part of Geoff's Sound Change Applier, version 0.8
# (August 2010). You can obtain the latest version of this program
# from http://gesc19764.pwp.blueyonder.co.uk/sca.html

from SCAdefs import *
from SCAitem import *

import random, string, yaml

##############################################################################

chartypes = yaml.load(file("SCAchars.yaml", "r"))

##############################################################################

""" This class encapsulates one of the four parts of a single rule -
BEFORE, AFTER, PRE, and POST. """

class SCARulePart:
    """ Construct this part from a string.
    parent: the SCARule of which this part is a part
    anchor: what '#' should be turned into
    s:      the string to construct the rule from
    before: True for BEFORE, False otherwise.
    """
    def __init__(self, parent, anchor, s, before = None):
        n, self.items, self.last, self.parent = 0, [], "", parent
        self.anchor, self.before = anchor, before
        self.text = s

        if len(s) == 0: return

        L = list(s)

        while len(L) > 0: self.doNext(L)

        self.addLast()

    """ Do something with the next character in the string. """
    def doNext(self, L):
        c = L.pop(0)

        if c in chartypes:
            H = chartypes[c]

            if not hasattr(self, "add_" + H["type"]):
                raise SCAException("No add function for %s", H["type"])

            getattr(self, "add_" + H["type"])(c, L, H)
            return

        # Uppercase characters might refer to categories,
        if not c.isupper():
            self.last += c # not a special character; just add it
            return

        if   self.parent.sca.hasDef("cat",  c):
            self.add(SCACategory, c, self.getQuants(L))
        elif self.parent.sca.hasDef("list", c):
            self.add(SCAList,     c, self.getQuants(L))
        else:
            self.last += c

    """ Remove any quantifiers from the string, and return them. """
    def getQuants(self, L):
        s = ""
        
        while len(L) > 0 and L[0] in '*+?': s += L.pop(0)

        return s

    """ Digits get converted to indexes. """
    def add_index(self, c, L, H):
        sign = ''

        if c == '-': sign, c = c, L.pop(0)

        if c in "123456789": self.add(SCAIndex, sign + c)
        else:
            L = [c] + L
            self.last += "-"

    """ Hash characters get turned into the appropriate regexp
    special character. """
    def add_anchor(self, c, L, H):
        if not self.anchor:
            raise SCAException("'#' is not allowed in BEFORE " +
                                       "or AFTER ")
        self.last += self.anchor

    """ Backslashes escape the following character. """
    def add_escape(self, c, L, H):
        if len(L) == 0: c = ' '
        else:           c = L.pop(0)

        if c in '.|?+*<[{%#': c = '\\' + c
        elif c == '\\': c += c

        self.last += c

    """ Some characters need to be escaped. """
    def add_special(self, c, L, H): self.last += '\\' + c

    """ Add a zero. """
    def add_zero(self, c, L, H): self.add(SCAZero, '')

    """ Add a part reference to BEFORE. """
    def add_part(self, c, L, H):
        if len(L) > 0 and L[0] in '123':
            self.items.append(SCAPartref(self.parent, 0, L.pop(0)))
        else:
            self.items.append(SCAPartref(self.parent, 0, "1"))

    """ Add a delimited item. """
    def add_delim(self, c, L, H):
        s, d = "", H['close']

        if d not in L: raise SCAException("No terminator '%s' found", d)

        while L[0] != d: s += L.pop(0)

        L.pop(0)
        quants = self.getQuants(L)

        self.add(globals()["SCA" + H['class']], s, quants)

    """ Add any leftover text as a single literal. """
    def addLast(self):
        if len(self.last) == 0: return

        self.items.append(SCALiteral(self.parent, len(self.items), self.last))
        self.last = ""

    """ Add the item to this part.
    C: the class of the item
    s: its text
    q: any quantifiers
    """
    def add(self, C, s, q = None):
        self.addLast() # very important

        if q is not None:
            self.items.append(C(q, self.parent, len(self.items),
                                s, not self.before))
        else:
            self.items.append(C(self.parent, len(self.items),
                                s, not self.before))

    """ Return the concatenation of calls to _func_ on each item. """
    def get(self, func):
        return "".join([getattr(I, func)() for I in self.items])

    def getExtRexp(self): return self.get("getExtRexp")
    def getRexp(self): return self.get("getRexp")
    def getText(self): return self.get("getText")

    """ Debugging function. """
    def showDetailed(self, header):
        print header
        for I in self.items: print "   ", I

    """ Return the _i_'th item in this part; _i_ may be negative. Note
    that the first item is at index 1, not 0, since 0 means 'zero'.
    """
    def __getitem__(self, i):
        if i < 0: return self.items[i]
        return self.items[i - 1]

    """ How many itenms are in this part? """
    def __len__(self): return len(self.items)

    """ Colour a character if necessary. """
    def colourChar(self, c):
        if c not in "<>[]|#%+*?$`": return c
        return cols(c, 33)

    """ Return the representation of this string, as text if b is True
    and as a regexp otherwise, with special characters coloured.
    """
    def colour(self, b):
        if b: s = self.text
        else: s = self.getRexp()

        return "".join([self.colourChar(c) for c in s])

""" This class is used for BEFORE and AFTER, which require more
functionality than PRE and POST. """

class SCAMatchingRulePart(SCARulePart):
    """ We need a special regexp to identify each item in BEFORE. """
    def __init__(self, parent, s, before):
        SCARulePart.__init__(self, parent, None, s, before)

        self.re = None

        if before:
            rexp = "".join(["(%s)" % I.getRexp() for I in self.items])
            self.re = re.compile(rexp)

    """ Convert the text which matches to a single item.
    R: the corresponding item in AFTER
    I: the item in BEFORE
    m: the matchitem which matched BEFORE
    groups: the matchitem which matched PRE-BEFORE-POST
    verbose: for debugging
    """
    def convertItem(self, R, I, m, groups, verbose):
        if not I.indexable(): return I.convert(None, None, None, None)

        if I.group is not None: return groups[I.group - 1]

        n = I.getRef()

        if n < 0: n += m.lastindex
        else:     n -= 1

        if len(m.groups()) > 0:
            old = m.groups()[n]
        else:
            old = ""

        if verbose: print cols(old, 33)

        s = I.convert(R, old, groups, m.groups())
        return self.parent.sca.evaluate(s)

    """ We've matched something, so we need to do the replacements.
    p: the rule of which this part is a part
    orig: the matchitem which matched PRE-BEFORE-POST
    verbose: for debugging
    """
    def convert(self, p, orig, verbose = False):
        s = orig.groups(1)[1] # this is what matched to BEFORE
        m = p.before.re.match(s)
        ret = ""

        if verbose:
            print "regexp matched", orig.groups()
            print "BEFORE matched", m.groups()
            print

        for i, I in enumerate(self.items):
            R = p.getPart(I.part) # normally BEFORE

            if verbose:
                print cols(I, 43)
                R.showDetailed("--------")

            t = self.convertItem(R, I, m, orig.groups(), verbose)

            if verbose:
                print "-> [" + t + "] <-"
                print

            ret += t

        return ret

##############################################################################

""" This class encapsulates a single rule.
"""

class SCARule:
    """ The constructor.
    sca:  the SCA object to which the rule belongs
    f:    the name of the file the rule was read from, if appropriate
    n:    the line number in the file, if appropriate
    s:    the text describing the rule
    last: the previous rule (may be None)
    verbose: for debugging
    """
    def __init__(self, sca, f, n, s, last, verbose = False):
        self.line, self.file, self.sca, self.text = n, f, sca, s
        self.name, self.assertions = None, []

        # Work out what BEFORE AFTER PRE POST are supopsed to be

        L = s.split()

        if len(L) == 0: raise SCAException("No dialects given")

        self.dialects = L.pop(0)

        if len(L) == 0: raise SCAException("No BEFORE part given")

        t = L.pop(0)

        if t[0] == '`':
            if t[1] == '@':
                before, after = sca.getRule(t[2:]).orig[0:2]
            else:
                before, after = sca.findDef('change', t[1:])
        else:
            before = t
            
            if len(L) == 0: raise SCAException("No AFTER part given")

            after = L.pop(0)
            
        if len(L) == 0: raise SCAException("No ENV part given")

        env = L.pop(0)

        if env[0] == '`':
            if env[1] == '@':
                env = sca.getRule(env[2:]).orig[2]
            else:
                env = sca.findDef('env', env[1:])

        if "_" not in env: raise SCAException("Missing '_' in environment")

        if before == '`':
            if last is None: raise SCAException("No previous rule")
            before = last.before

        if after == '`':
            if last is None: raise SCAException("No previous rule")
            after = last.after

        if env == '`':
            if last is None: raise SCAException("No previous rule")
            pre, post = last.pre, last.post
        else:
            pre, post = env.split("_")

        self.makeFlags(L)

        if pre == '%': pre, before = before, '%1'

        if   post == '%': post = '%2'
        elif post == '<': post = '%1'

        if after == "<": after = "%1"
        if after == ">": after = "%3"

        # Compile everything

        self.orig   = (before, after, pre + "_" + post)
        self.pre    = SCARulePart(self, "^", pre)
        self.post   = SCARulePart(self, "$", post)
        self.before = SCAMatchingRulePart(self, before, True)
        self.after  = SCAMatchingRulePart(self, after,  False)

        self.rexp = "".join(["(%s)" % P.getExtRexp()
                            for P in self.pre, self.before, self.post])

        if verbose:
            for i in ["before", "after", "pre", "post"]:
                getattr(self, i).showDetailed(i)
            print "Rexp:", self.rexp

        for I in self.after: I.validate(verbose)

        self.parts = (self.before, self.after, self.pre, self.post)

        self.re = re.compile(self.rexp)

    """ Interpret the flag strings. """ 
    def makeFlags(self, L):
        self.percent, self.banana, self.reverse, self.once, \
        self.persistent = None, False, False, False, False

        for s in L:
            if s[0] in "123456789":
                try:
                    self.percent = int(s)
                except ValueError, e:
                    raise SCAException("Invalid percentage: '%s'", s)
                if not 0 < self.percent < 100:
                    raise SCAException("Bad percentage: '%s'", s)
                continue

            if s[0] == '@':
                if len(s) == 1: raise SCAException("Bad rule name")
                self.name = s[1:]
                continue

            for c in s:
                if   c == 'B': self.banana = True
                elif c == 'F': self.once = True
                elif c == 'L': self.once, self.reverse = True, True
                elif c == 'R': self.banana, self.reverse = True, True
                elif c == 'P': self.persistent = True
                else: raise SCException("Unknown flag '%s'", c)

    """ Does this rule apply to dialect _d_? """
    def appropriate(self, d):
        return self.dialects == '*' or d in self.dialects

    """ Return PRE, BEFORE, or POST depending on _i_. BEFORE is the
    default.
    """
    def getPart(self, i):
        if i is None: return self.before
        return [self.pre, self.before, self.post][i]

    """ Return value _n_ from part _i_ as in getPart(). An exception
    is thrown if value _n_ does not exist or is not indexable.
    """
    def getItem(self, i, n):
        part = self.getPart(i)

        if n is None: return I.text

        if n < 0: n += len(part)

        if not 0 < n <= len(part):
#            part.showDetailed("-----------")
            f = "Bad index %d in map: part %d has length %d"
            raise SCAException(f % (n, i, len(part)))

        I = part[n]

        if not I.indexable():
            raise SCAException("Index %d in map is not indexable" % n)

        return I.text

    """ Return the regular expression from which the rule was
    compiled.
    """
    def getRexp(self): return self.rexp

    """ Return a sensible textual representataion of the rule. """
    def getText(self):
            T = tuple([P.getText() for P in self.parts])
            return "%s -> %s / %s_%s" % T

    """ Apply this rule to _word_ in dialect _d_, subject to exceptions
    in _E_. The return value is a tuple of a number and a string:
    - (0, result) if the rule was actually applied
    - (1, _word_) if the rule does not apply to _d_
    - (2, _word_) if _word_ and _d_ are an exception in _E_
    """
    def apply(self, d, word, E = None, verbose = False):
        if not self.appropriate(d): return 1, word

        if E is not None and E.isException(self.name, word, d):
            return 2, word

        if self.reverse: n, dn = len(word) - 1, -1
        else:            n, dn = False, 0

        w = word

        if verbose: print "Looking for:", self.re.pattern

        while True:
            m = self.re.match(w, n)
            if verbose: print "Matched:", w, n, m

            if m is not None:
                pre, before, post = m.groups()
                e = m.end()
                t = self.after.convert(self, m, verbose)
                w = w[:n] + pre + t + post + w[e:]

                if not self.reverse:
                    dn = len(pre) + len(t)
                    if not self.banana: dn += len(post)
            elif not self.reverse: dn = 1

            n += dn

            if self.reverse and n < 0: break
            if not self.reverse and n >= len(w): break

            if self.once and m: break

        return 0, w

    """ Add an assertion to this rule. The parameters must be, in
    order, the dialect, the word, and the expected result.
    """
    def addAssertion(self, *args): self.assertions.append(args)

    """ Apply this rule to some words.
    H: should map dialects to words
    E: exceptions
    P: persistent rules
    assert: True to run in assertion mode
    func: if given and not none, a callback function which is called
    with the following, in order:
    - the dialect
    - the return number from self.apply()
    - the original word, i.e. H[dialect]
    - the return string from self.apply()
    - True if the rule is persistent, False otherwise
    """
    def process(self, H, E, P, **extras):
        f = "Assertion failed at line %d of '%s':\n" +\
            "\texpected '%s', but got '%s'"

        if extras.get("doassert", False):
            for d, w, r in self.assertions:
                n, ret = self.apply(d, w)
                if ret != r:
                    raise SCAException(f, self.line, self.file, r, ret)

        for d in H.keys():
            oldword = H[d]

            self.sca.setLastWord(oldword)

            ret, newword = self.apply(d, oldword, E)

            if "func" in extras and extras["func"] is not None:
                extras["func"](self, d, ret, oldword, newword, P is None)

            H[d] = newword

    """ Return the rule in text form.
    b: True to return it like the input, False as a regexp
    c: True to colour it, False if not
    """
    def getShowText(self, b, c):
        if not c:
            if b: L = [ s.getText() for s in self.parts ]
            else: L = [ s.getRexp() for s in self.parts ]

            return "%s -> %s / %s_%s" % tuple(L)

        L = [ s.colour(b) for s in self.parts ]

        return L[0] + cols(" -> ", 36, c) +\
               L[1] + cols(" / ",  36, c) +\
               L[2] + cols("_",  36, c) + L[3]

##############################################################################

""" A class to represent headings, subheadings, and
subsubheadings. These are just displayed, and no actual processing is
done.
"""
class SCAHeading:
    """ The constructor.
    level: respectively 0, 1, 2
    text:  what is displayed
    """
    def __init__(self, level, text):
        self.level, self.text = level, text

    def process(self, H, E, P, **extras):
        if "func" in extras and extras["func"] is not None:
            extras["func"](self, None, self.level, self.text, None, True)

##############################################################################

""" Parameters for groups. The keys are the names of the parameters;
the value is a tuple containing the type, the default value, and any
other parameter-specific data.
"""
GroupParams = {
    "times":    ( "Int",    1,    1, 1000),
    "max":      ( "Int",    None, 1, 1000),
    "shuffle":  ( "Bool",   False),
    "pick":     ( "Int",    None, 1, 1000),
    "prob":     ( "Int",    None, 1, 100),
    "ruleprob": ( "Int",    None, 1, 100),
    "name":     ( "String", None),
    "reduce":   ( "Float",  None, 0, 1.0),
    }

##############################################################################

""" A class which represents the parameters which can be applied to
rule groups.
"""

class SCAGroupParams(dict):
    """ The constructor.
    H: currently GroupParams above; should really come from YAML.
    P: a list of tuples of the supplied parameters and their values
    clparams: variables defined on the command-line with -D
    """
    def __init__(self, H, P, clparams):
        dict.__init__(self)

        for param in H.keys(): self[param] = H[param][1]

        for param, value in P:
            if param not in H:
                raise SCAException("Unknown parameter '%s'" % param)

            T = H[param]

            if value[0] == '&':
                name, default = value[1:].split(":")

                if name in clparams: value = clparams[name]
                else: value = default

            f = getattr(self, "get" + T[0])
            if f is None:
                raise SCAException("Unknown parameter type '%s'" % T[0])

            self[param] = f(value, *T[2:])

    """ Get the value of parameter _s_ as an integer, and warn if it
    isn't between _n0_ and _n1_.
    """
    def getInt(self, s, n0 = None, n1 = None):
        try: n = int(s)
        except ValueError:
            raise SCAException("'%s' does not represent an integer", s)

        if n1 is not None and n > n1:
            raise SCAException("'%s' must be at least %d", s, n1)

        if n0 is not None and n < n0:
            raise SCAException("'%s' must be at most %d", s, n0)

        return n

    """ Get the value of parameter _s_ as a float, and warn if it
    isn't between _f0_ and _f1_.
    """
    def getFloat(self, s, f0 = None, f1 = None):
        try: f = float(s)
        except ValueError:
            raise SCAException("'%s' does not represent a float", s)

        if f1 is not None and f > f1:
            raise SCAException("'%s' must be at least %f", s, f1)

        if f0 is not None and f < f0:
            raise SCAException("'%s' must be at most %f", s, f0)

        return f

    """ Get the value of parameter _s_ as a string. """
    def getString(self, s): return s

    """ Return the value of parameter _s_ as a boolean. This actually
    sets it to True, since boolean parameters are False by default.
    """
    def getBool(self, s): return True

##############################################################################

""" A class which represents groups of rules. """

class SCARuleGroup:
    """ The constructor.
    sca: the SCA instance of which this rule group is a part
    H: command-line variables defined with -D
    params: a list tuples of parameters and values as supplied
    parent: the rule group of which this group is a part; None for the
    top-level group.
    """
    def __init__(self, sca, H, params = [], parent = None):
        self.rules  = []
        self.parent = parent
        self.sca    = sca
        self.params = SCAGroupParams(GroupParams, params, H)
        self.name   = self.params["name"]

        if self.params["pick"] is not None:
            self.params["shuffle"] = True
            self.params["max"] = self.params["pick"]

    ######################################################################

    """ Add a rule to this group. """
    def addRule(self, R): self.rules.append(R)

    """ Add a new subgroup with parameters _P_ and command-lien
    variables _H_ to this group.
    """
    def addGroup(self, sca, P, H):
        G = SCARuleGroup(sca, H, P, self)
        self.rules.append(G)
        return G

    """ Return True if a random percentage is less than the value of
    parameter _param_ and False otherwise. If the value of _param_ is
    None, True is returned also.
    """
    def proceed(self, param):
        n = self.params[param]
        b = n is None or random.randint(0, 99) < n
        r = self.params["reduce"]

        if r is not None and n is not None:
            self.params[param] = n * r / 100.0

        return b

    """ Apply the rules in this group to a word in one or more
    dialects.
    H: contains a word for each dialect
    E: exceptions
    P: persistent rules; should be None if this rule group is the one
    which contains the persistent rules, for obvious reasons
    other arguments: see SCARule.process()
    """
    def process(self, H, E, P, **extras):
        n, m = 0, self.params["max"]

        for i in range(self.params["times"]):
            if not self.proceed("prob"): continue

            if self.params["shuffle"]: random.shuffle(self.rules)

            for R in self.rules:
                if not self.proceed("ruleprob"): continue

                R.process(H, E, P, **extras)
                if P is not None: P.process(H, E, None, **extras)

                n += 1
                if m and n >= m: break

    """ Add a heading containing _text_ at _level_. """
    def addHeading(self, level, text):
        H = SCAHeading(level, text)
        self.rules.append(H)
        return H

    """ Add an assertion.  The parameters must be, in
    order, the dialect, the word, and the expected result.
    """
    def addAssertion(self, *args): self.rules[-1].addAssertion(args)

    """ Show all rules in this group; for debugging only.
    enc: the encoding to use
    """
    def showRules(self, enc):
        print "*** Group %s ***" % self.name

        for R in self.rules: print R.text.encode(enc)

##############################################################################
