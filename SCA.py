# This file is part of Geoff's Sound Change Applier, version 0.8
# (August 2010). You can obtain the latest version of this program
# from http://gesc19764.pwp.blueyonder.co.uk/sca.html

import traceback, yaml

from SCArule import *

defre     = re.compile("\s+=\s+")
listdefre = re.compile("\s+==\s+")

##############################################################################

""" This class is the base class for those which handle the various
types of definition. Subclasses need to implement parse().
"""

class SCADefinition():
    """ The constructor.
    name: a string which identifies instances; should be unique.
    parent: what this belongs to
    """
    def __init__(self, name, parent):
        self.defs, self.name, self.parent = {}, name, parent

    """ Is there a definition for _name_? """
    def has(self, name): return name in self.defs

    """ Return the definition corresponding to _name_, or None if
    there isn't one.
    """
    def get(self, name): return self.defs.get(name)

    """ Return the definition corresponding to _name_, throwing an
    exception if there isn't one.
    """
    def find(self, name):
        if not self.has(name):
            raise SCAException("Unknown %s '%s'", self.name, name)
        return self.get(name)

    """ Define _name_ as _s_; complain if it already has a definition.
    """
    def put(self, name, s):
        if name in self.defs:
            raise SCAException("%s '%s' has already been defined",
                               self.name, name)

        self.defs[name] = self.parse(s)

    """ Show all current definitions. """
    def showDefs(self):
        print "\nCurrent definitions for '%s':" % self.name
        for name in sorted(self.defs.keys()):
            print "  %s -> '%s'" % (name, self.defs[name])
        print

    """ How many definitions do we have? """
    def __len__(self): return len(self.defs)

    """ Convert _s_ to what it is supposed to represent, and make
    sure it's valid and meaningful.
    """
    def parse(self, s): pass

##############################################################################

""" Class for storing category definitions. """

class SCACatDefinition(SCADefinition):
    def __init__(self, *args):
        SCADefinition.__init__(self, "Category", *args)

    """ If _name_ is defined, return its definition, otherwise return
    _name_.
    """
    def getIfDefined(self, name):
        if self.has(name): return self.get(name)
        return name

    def parse(self, s):
        chars = ""

        for name in escapedSplit(s):
            if name != name.upper():
                chars += self.getIfDefined(name)
                continue

            n = sum([1 for c in name if self.has(c)])

            if n == 0: chars += name; continue

            if n != len(name):
                raise SCAException("Not all categories in '%s' are defined",
                                   name)
                
            for t in name: chars += self.get(t)

        return chars

""" Class for storing list definitions. """

class SCAListDefinition(SCADefinition):
    def __init__(self, *args):
        SCADefinition.__init__(self, "List", *args)

    def parse(self, s): return escapedSplit(s, ",")

""" Class for storing string definitions. """

class SCAStringDefinition(SCADefinition):
    def __init__(self, *args):
        SCADefinition.__init__(self, "String", *args)

    def parse(self, s): return s

""" Class for storing change (BEFORE and AFTER) definitions. """

class SCAChangeDefinition(SCADefinition):
    def __init__(self, *args):
        SCADefinition.__init__(self, "Change", *args)

    def parse(self, s):
        L = escapedSplit(s)

        if len(L) != 2:
            raise SCAException("There must be exactly 2 fields " +
                               "in a change definition")
        return L

""" Class for storing environment (PRE and POST) definitions. """

class SCAEnvDefinition(SCADefinition):
    def __init__(self, *args):
        SCADefinition.__init__(self, "Environment", *args)

    def parse(self, s):
        L = escapedSplit(s)

        if len(L) > 1:
            raise SCAException("There must be exactly 1 field " +
                               "in an environment definition")

        if "_" not in s:
            raise SCAException("There must be a '_' character " +
                               "in an environment definition")

        return s

""" Class for storing feature definitions. """

class SCAFeatureDefinition(SCADefinition):
    def __init__(self, *args):
        SCADefinition.__init__(self, "Feature", *args)

    def parse(self, s):
        L = s.split("|")

        if len(L) != 2:
            raise SCAException("There must be exactly two fields " +
                               "in a feature definition")

        neg = self.parsePart(L[0], "negative")
        pos = self.parsePart(L[1], "positive")

        if len(neg) != len(pos):
            raise SCAException("Length mismatch in feature definition")

        return neg, pos

    def parsePart(self, s, t):
        if len(s) == 0:
            raise SCAException("Empty %s part in feature definition", t)

        return ''.join([ self.parent.getCat(p) for p in s.split() ])

##############################################################################

""" This class encapsulates a set of sound changes together with
all related definitions and directives.
"""

class SCA():
    """ The constructor.
    defs: variables defined on the comamnd-line with -D
    enc:  the encoding
    """
    def __init__(self, defs = {}, enc = 'utf-8'):
        self.enc = enc

        # The last rule which was compiled.
        self.lastrule = None

        # A sensible default set of dialects.
        self.dialects = "A"

        # By default we don't want a dialect prefix.
        self.dp = ""

        # Rule counts.
        self.rules, self.prules = 0, 0

        # Flags for ignoring sections of the input file.
        self.skip, self.done = False, False

        # Various definitions
        self.defs, self.cldefs = {}, defs
        self.defs["cat"]     = SCACatDefinition(self)
        self.defs["list"]    = SCAListDefinition(self)
        self.defs["string"]  = SCAStringDefinition(self)
        self.defs["change"]  = SCAChangeDefinition(self)
        self.defs["env"]     = SCAEnvDefinition(self)
        self.defs["feature"] = SCAFeatureDefinition(self)

        # There are two special rule groups: one which contains the
        # persistent rules, and one which contains all the other rules
        # which aren't explicitly in another group.
        self.main = SCARuleGroup(self, defs)
        self.activegroup = self.main
        self.persistent = SCARuleGroup(self, defs)

        # Files we're currently including.
        self.files = set([])

        # Parameters for directives.
        self.dirparams = yaml.load(file("SCAdirparams.yaml", "r"))

        # Exceptions, amazingly.
        self.exceptions = SCAExceptionWords()

        # Allow us to find specific rules easily.
        self.namedrules = {}

        # If this is not None, "random" numbers will be seeded with it.
        self.lastword = None

    ######################################################################

    """ Return the SCADefinition corresponding to _deftype_, or
    complain if there isn't one.
    """
    def getDefinition(self, deftype):
        if deftype not in self.defs:
            raise SCAException("Invalid definition type '%s'", deftype)
        return self.defs[deftype]

    """ Define _name_ as _value_ in _deftype_. This means that the
    same name can have different definitions in different definition
    types.
    """
    def addDef(self, deftype, name, value):
        self.getDefinition(deftype).put(name, value)

    """ Is _name_ defined in _deftype_? """
    def hasDef(self, deftype, name):
        return self.getDefinition(deftype).has(name)

    """ Return the definition for _name_ in _deftype_. """
    def getDef(self, deftype, name):
        return self.getDefinition(deftype).get(name)

    """ Return the definition for _name_ in _deftype_, and throw an
    exception if there isn't one.
    """
    def findDef(self, deftype, name):
        return self.getDefinition(deftype).find(name)

    ######################################################################

    """ If _s_ equals '$string', return the correpsonding definition,
    otherwise return _s_. This is a leftover from a more general
    evaluation function.
    """
    def evaluate(self, s):
        if s == '': return ''

        if s[0] == '$':
            return self.evaluate(self.getDef("string", s[1:]))

        return s

    """ Convert a category specfication in _cat_ to a list of symbols
    which will be used in a regexp. For example, if 'A' is defined as
    'abcde' and 'B' is defined as 'defgh', then the following values
    of _cat_ will generate the following lists:

    'A+efg'         [abcdefg]
    'A-de'          [abc]
    'A+B' or 'AB'   [abcdefgh]
    'A-B'           [abc]
    '^A' or '-A'    [^abcde]
    """
    def getCat(self, cat):
        L = re.split("([-+^])", cat)

        if len(L) == 0: return ""

        chars, add, first, comp = [], True, True, False

        while len(L) > 0:
            s = L.pop(0)

            if s == '': continue
            if s == '^' and first: comp, first = True, False; continue
            if s == '+': add, first = True,  False; continue
            if s == '-':
                if first and len(L) == 1: return "^" + L[0]
                add, first = False, False
                continue

            t = self.defs["cat"].parse(s)

            if t is None:
                if first:
                    raise SCAException("Unknown category '%s'", s)
                else:
                    t = s

            if add: chars += t
            else:   chars = [ c for c in chars if c not in t ]

            first = False

        s = "".join(chars)

        if comp: return "^" + s

        return s

    ######################################################################

    """ Obey a directive as given in _line_.  There may be a better
    way to so this with regexps, but this will have to do for now.
    """
    def doDirective(self, line):
        L, P = escapedSplit(line), []

        name = L.pop(0)

        try:
            f = getattr(self, "dir_" + name)
        except AttributeError:
            raise SCAException("Unknown directive '%s'", name)

        if "heading" in name: f(" ".join(L)); return

        for s in L:
            a = escapedSplit(s, '=', 2)

            if len(a) == 1: P.append((s, None))
            else:           P.append(tuple(a))

        if name not in self.dirparams: f(P); return

        H = self.PtoH(name, P)

        pnames = [ h["name"] for h in self.dirparams[name] ]
        params = [ H[s] for s in pnames ]

        f(*params)

    """ Dummy directive function; this just shows its parameters and
    their values. Useful for seeing how the directive line is being
    parsed.
    """
    def dir_directive(self, P):
        for param, value in P:
            print "%s -> %s" % (param, value)

    """ Convert a list of (param, value) tuples in _L_, which came
    from parameters to directive _name_, to a dictionary, which is
    returned.
    """
    def PtoH(self, name, L):
        H, Hparams = {}, {}

        for k, v in L: Hparams[k] = v

        for P in self.dirparams[name]:
            p, v = P["name"], P.get("default", None)

            if p not in Hparams:
                raise SCAException("Parameter '%s' not given for '%s'",
                                   p, name)

            if p in Hparams: v = Hparams[p]

            if v is None:
                raise SCAException("No value for parameter '%s' in '%s'",
                                   param, name)

            H[p] = v
            del Hparams[p]

        for k in Hparams.keys():
            raise SCAException("Unknown parameter '%s' in '%s'", k, name)

        return H

    """ Declare our dialects. """
    def dir_dialects(self, P):
        self.dialects = ""

        for p, v in P: # v is ignored
            if not p.isalnum():
                raise SCAException("Bad dialect spec '%s'", p)

            for c in p:
                if c in self.dialects:
                    raise SCAException("Duplicate dialect spec '%s'", c)

                self.dialects += c

        if self.dialects == '':
            raise SCAException("No dialects given")

    """ Read from file _s_. """
    def dir_include(self, s): self.readFromFile(s)

    """ Set the seed to _s_. """
    def dir_seed(self, s):
        if   s == 'time': random.seed()
        elif s == 'word': self.lastword = ''
        else:             random.seed(s)

    """ Set the dialect prefix, which is prepended to each subsequent
    line, to _s_. _s_ should be empty to turn this off.
    """
    def dir_dirprefix(self, s):
        for c in s:
            if c not in self.dialects:
                raise SCAException("Unknown dialect '%s'", c)

        self.dp = s

    """ Define a new group with parameters _P_. """
    def dir_group(self, P):
        self.activegroup = self.activegroup.addGroup(self, P, self.cldefs)

    """ End the definition of the current group.
    _P_: ignored, but needed for consistency
    """
    def dir_endgroup(self, P):
        self.activegroup = self.activegroup.parent

        if self.activegroup is None:
            raise SCAException("No active group")

    """ Add a heading with text in _s_. """

    def dir_heading(      self, s): self.activegroup.addHeading(0, s)
    def dir_subheading(   self, s): self.activegroup.addHeading(1, s)
    def dir_subsubheading(self, s): self.activegroup.addHeading(2, s)

    """ Add an assertion. The arguments must be, in order, the
    dialect, the word, and the expected result.
    """
    def dir_assert(self, *args):
        self.activegroup.addAssertion(*args)

    """ Add an exception. See SCAExceptionWords.add() for the
    arguments.
    """
    def dir_exception(self, *args): self.exceptions.add(*args)

    """ Read in exceptions from _s_. """
    def dir_exceptfile(self, s):
        self.exceptions.readFromFile(s, self.enc)

    """ We want to skip subsequent lines. """
    def dir_skip(self, *args): self.skip = True

    """ We want to stop skipping subsequent lines. """
    def dir_noskip(self, *args): self.skip = False

    """ We want to skip all subsequent lines. """
    def dir_end(self, *args): self.done = True

    """ We want to skip subsequent lines if a variable is defined.
    """
    def dir_skipif(self, cond): self.skip = cond in self.cldefs

    """ We want to skip subsequent lines unless a variable is defined.
    """
    def dir_skipunless(self, cond): self.skip = cond not in self.cldefs

    ######################################################################

    """ Compile _s_ into a rule, directive, or definition.
    f n: the name of the file and the line number from where the
    string wasread from; may be something else if you're doing this by
    hand.
    """
    def compile(self, f, n, s):
        if self.skip and s not in "!noskip" and s not in "!end":
            return

        if s[0] == '!':
            self.doDirective(s[1:])
            return

        if " = " in s:
            name, value = defre.split(s, 1)
            self.addDef("cat", name, value)
            return

        L = s.split()
        if L[0] in self.defs:
            self.addDef(L[0], L[1], " ".join(L[2:]))
            return
        
        if len(self.dp) > 0: s = self.dp + " " + s

        R = SCARule(self, f, n, s, self.lastrule) #, verbose)

        if R.name is not None:
            if R.name in self.namedrules:
                raise SCAException("Rule '%s' islaready defined",
                                   R.name)
            self.namedrules[R.name] = R

        if R.persistent:
            self.persistent.addRule(R)
            self.prules += 1
        else:
            self.activegroup.addRule(R)
            self.rules += 1

        self.lastrule = R

    """ Read rules, definitions, and so on from a file.
    f: the name of the file
    enc: its encoding
    """
    def readFromFile(self, f):
        if f is None:
            raise SCAException("No sound change file given")
            
        if f[-4:] != '.sca': f += '.sca'

        if f in self.files:
            raise SCAException("File is already being included")

        self.files.add(f)

        for s, n in readfile(f, self.enc):
            try:
                self.compile(f, n, s)
            except SCAException, e:
                raise SCAException("At line %d of '%s':\n  %s", n, f, e.s)

            if self.done: break

        self.done, self.skip = False, False
        self.files.remove(f)

    ######################################################################

    """ Process _word_ through all the rules, in _dialects_.
    See SCARule.process() for the extra arguments.
    """
    def process(self, word, dialects = None, **extras):
        if dialects is None: dialects = self.dialects

        H = { }

        self.setLastWord(word)

        for d in dialects: H[d] = word

        self.main.process(H, self.exceptions, self.persistent, **extras)

        return H

    """ Show all rules; for debugging. """
    def showRules(self): self.main.showRules(self.enc)

    """ Return the rule named by _name_, and throw an exception if it
    doesn't exist.
    """
    def getRule(self, name):
        if name not in self.namedrules:
            raise SCAException("No rule is called '%s'", name)

        return self.namedrules[name]

    """ Return a string which says how many of each thing there are. """
    def getCounts(self):
        s = "rules: %d  persistent: %d  " % (self.rules, self.prules)

        for t in [ "string", "cat", "list", "change", "env" ]:
            s += "%ss: %d  " % (t, len(self.getDefinition(t)))

        return s + "\n"

    """ Display all current definitions. """
    def showDefs(self):
        for param in sorted(self.defs.keys()):
            self.getDefinition(param).showDefs()

    """ Set the last word to _word_, which will be used to seed
    the pseudo-random number generator.
    """
    def setLastWord(self, word):
        if self.lastword is None: return

        self.lastword = word
        random.seed(self.lastword)

##############################################################################
