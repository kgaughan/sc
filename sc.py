# Geoff's Sound Change Applier version 0.5 (March 2009)
# First created by Geoff Eddy, from an idea by Mark Rosenfelder
# You may obtain this from http://www.cix.co.uk/~morven/lang/sc.html
#
# You may use this program for any purpose provided that you credit
# the author(s) appropriately, do not restrict what others can do with
# it, and do not sell it or allow it to be sold.

##############################################################################

from scrule import *

# Regexps and other things for deprecated features

oldmapre1  = re.compile('#(-?\d)`(\w+)`(\w+?)(_|\s)', re.UNICODE)
oldmapre2  = re.compile('(<|>)`(\w+)`(\w+?)(_|\s)', re.UNICODE)

NONE, BACKQ, TILDE = 0, 1, 2

deprecations = [
    ( "~",   " ",    TILDE, "Tildes are deprecated (use spaces)" ),
    ( "`>",  "{>}",  BACKQ, "Backquotes are deprecated (use {})" ),
    ( "`<",  "{<}",  BACKQ, "Backquotes are deprecated (use {})" ),
    ( "`%>", "{%>}", BACKQ, "Backquotes are deprecated (use {})" ),
    ( "`%<", "{%<}", BACKQ, "Backquotes are deprecated (use {})" ),
    ( oldmapre1, lambda m: "{%s:%s:%s}%s" % m.groups(),
      BACKQ, "Backquotes are deprecated (use {})" ),
    ( oldmapre2, lambda m: "{%s:%s:%s}%s" % m.groups(),
      BACKQ, "Backquotes are deprecated (use {})" ),
    ]

# Should be obvious

english = [ ( "PRE", "<" ), ("POST", ">"), ("BEFORE", "%") ]

##############################################################################

# This class implements a series of sound change rules.

class SC:
    def __init__(self, s, enc):
        self.changes    = []
        self.pchanges   = []
        self.conditions = []
        self.cats       = {}
        self.envs       = {}
        self.dialects   = '0'
        self.skip       = False

        n = s.rfind("/")
        if n < 0: self.dir = ""
        else:     self.dir = s[:n + 1]

        self.readfile(s, enc)

    # Read the sound changes in from a file.
    # FIXME: perhaps do running counts?
    def readfile(self, s, enc):
        n, f, last = 0, codecs.open(s, 'r', enc), None

        deps = NONE

        for line in f.readlines():
            line = line.strip()
            n += 1

            # skip empty lines
            if len(line) == 0: continue

            # skip comments
            if line[0] in '#!':
                if line[:2] == "#:":
                    self.changes.append(Comment(line[1:]))
                continue

            # remove !comments
            if '!' in line: line = line[:line.index("!")].strip()

            if line[:3] == 'END': break

            # skip other sections if necessary
            if line[:4] == 'SKIP':
                L = line[4:].split()
                
                if len(L) == 0:
                    self.skip = True
                    continue

                c = L.pop(0)
                if c not in [ 'if', 'unless']:
                    die(n, "Unknown word '%s' after SKIP", L[0])

                if len(L) == 0: die(n, "No condition after SKIP")
                if len(L) >  1: die(n, "Too many words after SKIP")

                cond = L.pop(0)
                self.skip = (cond in self.conditions) == (c == 'if')
                continue

            if line[:6] == 'NOSKIP':
                self.skip = False
                continue

            if self.skip: continue

            for old, new, flag, mesg in deprecations:
                if type(old) == type(""):
                    if not old in line: continue
                    line = line.replace(old, new)
                else:
                    if not old.search(line): continue
                    line = old.sub(new, line)
                
                if deps & flag: continue

                deps |= flag
                warn(n, mesg)

            for old, new in english: line = line.replace(old, new)

            # new category
            if re.search('=', line):
                self.defineCat(line, n, enc)
                continue

            # sound change
            try: c = SoundChange(line, self, last)
            except scException, e: die(n, "%s", e)

            if "P" in c.flag: self.pchanges.append(c)
            else:             self.changes.append(c)

            last = c

        f.close()

    # Add a new category; also take care of special categories.
    def defineCat(self, s, n, enc):
        (cat, val) = re.split("\s+=\s+", s)

        if string.lower(cat) == 'dialects':
            self.dialects = val
            return

        if string.lower(cat) == 'conditions':
            self.conditions = val.split()
            return

        if string.lower(cat) == 'include':
            self.readfile(self.dir + val, enc)
            return

        if cat[0] == '@':
            env = cat[1:]
            if env in self.envs:
                die(n, "Environment '%s' already defined", env)
            self.envs[env] = val
            return

        for c in cat:
            if c in string.punctuation:
                die(n, "Category name '%s' contains punctuation", cat)
            if c in string.whitespace:
                die(n, "Category name '%s' contains whitespace", cat)

        if len(cat) == 1:
            if cat != cat.upper():
                die(n, "Single-character category name '%s' " +
                    "is not uppercase", cat)
            for k, v in self.cats.iteritems():
                if cat in v:
                    die(n, "'%s' is used in category '%s'", cat, k)

        for c in val:
            if c in string.punctuation and c != '~':
                die(n, "Category value '%s' contains punctuation", val)

        if self.cats.has_key(cat):
            die(n, "Category '%s' already defined", cat)

        L, val = re.split('\s|~', val), ''

        for i in L:
            if i in self.cats: val += self.cats[i]
            else:              val += i

        self.cats[cat] = val

    # Find a category, or die if it doesn't exist.
    def getCat(self, cat, b = True):
        if cat in self.cats: return self.cats[cat]
        if not b: return None
        raise scException("Unknown category '%s'", cat)

    # Convert a match object from catre to "[sounds]".
    def catmatch2re(self, m):
        comp, cat, t, extra = m.groups()

        if t == "":
            s = self.getCat(extra)
            return "[" + comp + s + "]"

        if comp != "": raise scException("%s: Can't mix ^ and +-", s)

        if cat == "":
            if t == "+": return "[" + extra + "]"
            return "[^" + extra + "]"

        s = self.getCat(cat)

        if t == "+": s += "".join([c for c in extra if c not in s])
        else:        s  = "".join([c for c in s if c not in extra])

        return "[" + s + "]"

    # Convert "<cat>", "<cat+foo>", and "<cat-foo>" to "[sounds]".
    def cat2re(self, s):
        if s == s.upper() and s in self.cats:
            return "[" + self.cats[s] + "]"

        m = catre.match("<" + s + ">")
        if m is not None: return self.catmatch2re(m)
        raise scException("Cannot match '%s'", s)

    # Convert <<cat1,cat2>> and "<<CATS>>" to "[sounds]".
    def multicat2re(self, p):
        s = ""

        for t in p.split(":"):
            if   t in self.cats: s += self.cats[t]
            elif t == t.upper():
                for c in t:
                    if not c in self.cats:
                        self.die("%s: unknown category %s", p, c)
                    s += self.cats[c]
            else: self.die("%s: unknown category %s", p, t)

        return "[" + s + "]"

    # Is a sound change appropriate for one or more _dialects_?
    def appropriate(self, c, dialects):
        for d in dialects:
            if c.appropriate(d): return True

        return False

    # Yield all the appropriate changes and comments in the order in
    # which they should be applied.
    def get_changes(self, dialects, hlev):
        for c in self.changes:
            if not self.appropriate(c, dialects): continue
            yield c

            for p in self.pchanges:
                if not self.appropriate(p, dialects): continue
                yield p

    # Return the results of applying _word_ in _dialects_.
    #
    # hlev: how deep to print comments
    # col:  True to print in colour
    # v:    whether to print rules as suppled (1) or as regexps (2)
    # all:  True to show all rules, False to show only those with an effect
    # enc:  encoding
    def process(self, word, dialects, hlev = -1, col = False, v = -1,
                all = False, enc = "utf-8"):
        H = {}

        for d in dialects: H[d] = word

        if v >= 0: print cols("> ", 43, col) + word.encode(enc)

        for c in self.get_changes(dialects, hlev):
            for d in dialects:
                w = c.apply_and_print(d, H[d], hlev, col, v, all, enc)
                if w: H[d] = w

        for d in dialects:
            if v >= 0: print (cols(d, 43, col) + ' ' + H[d]).encode(enc)

        return H

    # Ditto, without printing and in dialect _d_ only.
    def process_single(self, word, d):
        for c in self.changes:
            word = c.apply(word, d)
            for p in self.pchanges: word = p.apply(word, d)

        return word

##############################################################################
