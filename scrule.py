# Geoff's Sound Change Applier version 0.5 (March 2009)
# First created by Geoff Eddy, from an idea by Mark Rosenfelder
# You may obtain this from http://www.cix.co.uk/~morven/lang/sc.html
#
# You may use this program for any purpose provided that you credit
# the author(s) appropriately, do not restrict what others can do with
# it, and do not sell it or allow it to be sold.

##############################################################################

# The classes in this file implement sound-change rules.

from scdefs import *
from scconv import *

import string
import re
import codecs

# Special regexps

indexre    = re.compile('#-?\d+')
envre      = re.compile('@(\w+)',                     re.UNICODE)
multicatre = re.compile('<<(\w|:)+>>',                re.UNICODE)
catre      = re.compile('<(\^?)(\w*?)([-+]?)(\w+?)>', re.UNICODE)
mapre      = re.compile('\{[-1-9<>%]:\w+:\w+\}',      re.UNICODE)
shortmapre = re.compile('\{[1-9<>%][<>]?\w*\}',       re.UNICODE)
mapre3     = re.compile('\{[1-9<>]\w\w\}',            re.UNICODE)

# Regexp-to-conversion mapping

MatchTypes = [
    ( indexre,    "Index" ),
    ( catre,      "Cat" ),
    ( mapre,      "Map" ),
    ( mapre3,     "Map3" ),
    ( shortmapre, "ShortMap" ),
]

##############################################################################

# Base class for rules; nothing special.

class Rule:
    def __init__(self, d): self.d = d

    def apply(self, word, d): return word

    # Does this rule apply to dialect _d_?
    def appropriate(self, d): return self.d == '*' or d in self.d

    # A convenient way to end it all.
    def die(self, s, *args): raise scException(s, *args)

##############################################################################

# Comments, which do no conversion but need to be printed if
# necessary.

class Comment(Rule):
    def __init__(self, s):
        L = s.split()
        s = L.pop(0)

        i = 0
        while i < len(s) and s[i] == ':': i += 1

        self.level, d, self.text = i, s[i:].strip(), " ".join(L)

        Rule.__init__(self, d)

    def to_string(self, level, colour):
        if not colour: return "--" + self.text + "--"
        return cols(self.text, 45)

    def apply_and_print(self, d, word, hlev, col, v, all, enc):
        if hlev >= self.level: print self.to_string(hlev, col)

##############################################################################

# Actual sound changes.

class SoundChange(Rule):
    def __init__(self, s, p, last):
        self.p, self.rule, uselastenv = p, [], False

        L = string.split(s.rstrip())

        # Ensure the dialects are sane.

        if len(L) == 0: self.die("No fields on line")

        Rule.__init__(self, L.pop(0))

        for c in self.d:
            if c in '.*': continue
            if c not in self.p.dialects:
                self.die("Unknown dialect '%s'", c)

        # Set up BEFORE.

        if len(L) == 0: self.die("No BEFORE field given")

        before = L.pop(0)

        if '0' in before and before != '0':
            self.die("'0' is only valid by itself in BEFORE")

        if '`' in before:
            if before not in ('`', '``'):
                self.die("'`' is only valid singly or doubled in BEFORE")
            if last is None:
                self.die("Can't use '`' or '``' in BEFORE in first rule")

            if before == '``': uselastenv = True
            before = last.rule[0]

        self.rule.append(before[:])

        # Save AFTER for later.

        if len(L) == 0: self.die("No AFTER field given")

        after, haveCat = L.pop(0), False
        after = after.replace("_", "")
        self.rule.append(after[:])

        # Now do the environment.

        if   uselastenv:  pre, post = last.rule[2:4]
        elif len(L) == 0: self.die("No environment field given")
        else:
            env = L.pop(0)
            if '`' in env:
                if env != '`':
                    self.die("'`' is only valid singly in ENV")
                pre, post = last.rule[2:4]
            else:
                c = string.count(env, '_')
                if c == 0: self.die('No environment (_) specified')
                if c  > 1: self.die('Too many _ characters')

                pre, post = string.split(env, '_')

        self.rule.append(pre[:])
        self.rule.append(post[:])

        pre  = pre.replace( '#', '^')
        post = post.replace('#', '$')

        if pre == '%': (pre, before) = (before, '\\1')

        post = post.replace('%', '\\2')
        if post == '<': post = '\\1'

        # Create the regexp objects.

        t = '%s_%s_%s' % (pre, before, post)

        before = self.convertcats(before)
        pre    = self.convertcats(pre)
        post   = self.convertcats(post)

        s = '(%s)(%s)(%s)' % (pre, before, post)

        try:
            self.re   = re.compile(s, re.UNICODE)
        except:
            self.die("%s -> %s: could not compile", t, s)
        
        # Convert AFTER.

        self.after = self.makeAfter(after)
        after = "".join(C.rexp() for C in self.after)
        self.rexp = before, after, pre, post

        # Finally, get the flags, if any.

        self.flag = "".join(L)

    # Get the elements of the rule and regular expression, coloured if
    # necessary.
    def colour(self, T, col):
        if not col: return "%s -> %s / %s_%s" % T

        s  = colourcat(T[0]) + cols(" -> ", 36)
        s += colourcat(T[1]) + cols(" / ",  36)
        s += colourcat(T[2]) + cols("_",    36)
        s += colourcat(T[3])

        return s

    # Convert "<abc>" and "T" to "abc" and "T"; do not allow anything
    # else.
    def reduceCat(self, s):
        if s[0] == "<" and s[-1] == ">": return s[1:-1]
        if len(s) == 1 and s == s.upper(): return s
        self.die("%s: bad cat spec", s)

    # Straightforward functions to add conversion types to AFTER.
    def addIndex(self, s): return Index(s, self.p)
    def addChar( self, s): return Char( s, self.p)
    def addMap(  self, s): return Map(  s, self.p)

    # Generate a mapping from a source and two cat specs.
    def genericMap(self, t, c1, c2):
        s1 = self.reduceCat(c1)
        s2 = self.reduceCat(c2)

        return Map("{%s:%s:%s}" % (t, s1, s2), self.p)

    # Take care of abbreviated mappings: > < %> %< n> n<
    def addShortMap(self, s):
        before, after, pre, post = self.rule
        s = s[1:-1]

        if not 1 <= len(s) <= 2: self.die("'%s': bad map format", s)

        if s == ">":  return self.genericMap(s,   post, before)
        if s == "<":  return self.genericMap(s,   pre,  before)
        if s == "%>": return self.genericMap("%", post, before)
        if s == "%<": return self.genericMap("%", pre,  before)

        if len(s) == 2 and s[0] in '123456789':
            i = int(s[0]) - 1
            t = before[i]
            if s[1] == ">": return self.genericMap(i, t, post)
            if s[1] == "<": return self.genericMap(i, t,  pre)
            self.die("'%s': bad map format", s)

        self.die("'%s': bad map format", s)

    # Generate a mapping from "{>AB}" and similar
    def addMap3(self, s): return self.genericMap(s[1], s[2], s[3])

    # Convert a single cat in each of BEFORE and AFTER to a mapping.
    def addCat(self, s): return self.genericMap("%", self.rule[0], s)

    # Generate AFTER from _s_.
    def makeAfter(self, s):
        L = []

        if s == '0': return []

        while len(s) > 0:
            m, C = self.findMatch(s)

            if m is None: n = 1
            else: n = m.end()

            t, s = s[:n], s[n:]
            L.append(C)

        return L

    # Convert _s_ to the appropriate conversion.
    def findMatch(self, s):
        for rexp, t in MatchTypes:
            m = rexp.match(s)
            if m is None: continue

            f = getattr(self, "add" + t)
            return m, f(s)

        c = s[0]

        if c == c.upper() and c in self.p.cats:
            return None, self.addCat(c)

        return None, self.addChar(c)

    # Convert BEFORE, PRE, and POST to the appropriate regexps.
    def convertcats(self, s):
        if s == '0': return ""

        s = envre.sub(self.getenv, s)
        s = multicatre.sub(self.multicat, s)
        s, t = catre.sub(self.p.catmatch2re, s), ""

        inb = False

        for c in s:
            if inb:
                t += c
                if c == ']': inb = False
            elif c == '[':
                t += c
                inb = True
            elif c == c.upper() and c in self.p.cats:
                t += "[" + self.p.cats[c] + "]"
            else:
                t += c

        return t

    # Convert "<<>>" to the appropriate regexp.
    def multicat(self, m): return self.p.multicat2re(m.group(0)[2:-2])

    # Convert "@env" to the appropriate regexp.
    def getenv(self, m):
        env = m.group(0)

        if env[0] == '@': env = env[1:]

        if not env in self.p.envs:
            self.die("Unknown environment '%s'", env)

        return self.p.envs[env]

    # Apply this sound change to a word, and return the result.
    def convert(self, m):
        pre, before, post = m.groups()
        after = "".join([c.convert(before, pre, post) for c in self.after])
        return pre + after + post

    # Find the last matching string of this sound change in s.
    def findlastmatch(self, s):
        n = len(s) - 1

        while n >= 0:
            m = self.re.match(s[n:])
            if m is not None: return n, m

            n -= 1

    # Apply this sound change to a word, but starting at the end.
    def reversebanana(self, s):
        while True:
            T = self.findlastmatch(s)
            if T is None: break

            n, m = T
            s = s[:n + m.start()] + self.convert(m) + s[n + m.end():]

        return s

    # Apply this sound change to a word and return the result.
    def apply(self, s, d):
        if not self.appropriate(d): return s

        if "R" in self.flag: return self.reversebanana(s)

        while True:
            t = self.re.sub(self.convert, s)
            if not "B" in self.flag: break
            if s == t: break

            s = t

        return t

    # Apply this sound change and print it if necessary
    def apply_and_print(self, d, word, hlev, col, v, all, enc):
        w = self.apply(word, d)

        if not all and w == word: return w

        if v <= 0: return w

        if   v == 1: t = self.colour(self.rule, col)
        elif v == 2: t = self.colour(self.rexp, col)

        if col:
            s = cols(d, 32) + " "

            if w == word or not all: s += "%-20s" % w
            else:
                s += cols(w, 44) + " " * (20 - len(w))
        else:
            s = "%s: %-20s" % (d, w)

        print (s + t).strip().encode(enc)

        return w

##############################################################################

