# Geoff's Sound Change Applier version 0.5 (March 2009)
# First created by Geoff Eddy, from an idea by Mark Rosenfelder
# You may obtain this from http://www.cix.co.uk/~morven/lang/sc.html
#
# You may use this program for any purpose provided that you credit
# the author(s) appropriately, do not restrict what others can do with
# it, and do not sell it or allow it to be sold.

##############################################################################

# This file contains the command-line interface.

banner = "Geoff's Sound Change Applier, version 0.5 (March 2009)"
info1  = "You can obtain the latest version of this program"
info2  = "from http://www.cix.co.uk/~morven/lang/sc.html"

shortargs = "c:l:d:s:e:arRmf:CqF:t:h:"
longargs  = [ "scfile=", "input=", "dialects=", "sep=", "enc=",
              "all", "rules", "regexp", "minimal", "field=",
              "colour", "quiet", "insep=", "testfile=", "hlevel=" ]

##############################################################################

from sc import *
import sys
import codecs
import getopt

def die(n, s, *args):
    sys.stderr.write(s % args + "\n")
    sys.exit(n)

##############################################################################

class clopthandler:
    def __init__(self, short, long):
        self.H = {}

        try: opts, args = getopt.getopt(sys.argv[1:], short, long)
        except getopt.GetoptError, err:
            self.usage()
            die(2, err)

        for o, a in opts: self.H[o] = a
        self.A = args

    def usage(self):
        print "\nPlease see the file sc.html for the correct usage."

    def __getitem__(self, a):
        for k in a:
            if self.H.has_key(k): return self.H[k]

##############################################################################

def showBanner(banner, lexfile):
    n = len(banner)
    s1 = "*" * n
    s2 = " " * n

    L = [s1, s2, banner, info1.center(n), info2.center(n), s2, s1]

    for s in L:
        sys.stderr.write(cols("* " + s + " *", 44) + "\n")

    if lexfile:
        sys.stderr.write("\nProcessing %s with %s.\n\n" % (lexfile, scfile))
    else:
        sys.stderr.write("\nUsing " + scfile + ".\n\n")

##############################################################################

def parsefields(s):
    if s is None: return None

    L = []

    for i in s.split(","):
        if "-" not in i:
            try: n = int(i)
            except ValueError:
                die(2, "Bad field argument: \"%s\" is not a number", i)
            if n not in L: L.append(n)
            continue
        
        a = i.split("-")

        if len(a) != 2:
            die(1, "Bad field range argument \"%s\"", i)
        try: start = int(a[0])
        except ValueError:
            die(1, "Bad field argument \"%s\": " +
                "\"%s\" is not a number", a[0])
        try: end = int(a[1])
        except ValueError:
            die(1, "Bad field argument \"%s\": " +
                "\"%s\" is not a number", a[i])
        if(start > end):
            die(1, "Bad field range endpoints \"%s\": ", i)

        for n in xrange(start, end + 1):
            if n not in L: L.append(n)

    L.sort()
    return L

##############################################################################

def processNormal(sc, word, dialects, opts):
    rexp = opts["-R", "--regexp" ] is not None
    rule = opts["-r", "--rules"  ] is not None
    col  = opts["-C", "--colour" ] is not None
    all  = opts["-a", "--showall"] is not None
    hlev = opts["-h", "--hlevel" ]

    if hlev is not None: hlev = int(hlev)
    else:                hlev = 0

    if   rule: v = 1
    elif rexp: v = 2
    else:      v = 0

    sc.process(word, dialects, hlev, col, v, all, enc)

def processAll(sc, word, dialects, opts, sep = None):
    if sep:
        H = sc.process(word, dialects)
        a = [word] + [H[d] for d in dialects]
        print string.join(a, sep).encode(enc)
    elif opts["-m", "--minimal"] is not None:
        H = sc.process(word, dialects)
        a = [H[d] for d in dialects]
        print string.join(a, " ").encode(enc)
    else:
        processNormal(sc, word, dialects, opts)

##############################################################################

def doTestFile(sc, testfile, insep, col, m):
    n, first = 0, True
    f = codecs.open(testfile, 'r', enc)

    for s in f.readlines():
        if first: # have to do it this way
            a = s.strip().split(insep)

            if not "in" in a: die(1, "No input field given in header + "
                                  "of %s.\n", testfile)
            first = False
            continue

        L     = s.strip().split(insep)
        word  = L[a.index("in")]
        words = sc.process(word, sc.dialects)

        if m:     t = ""
        elif col: t = colour(word, 33) + colour(" -> ", 32)
        else:     t = "%s -> " % word

        for d in a:
            if d not in words: continue

            w1, w2 = words[d], L[a.index(d)]
            if w1 != w2: n += 1

            if m:
                if w1 == w2: continue
                if col:
                    t += colour(d, 35) + colour(": ", 32)
                    t += colour(word, 33) + colour(" -> ", 32)
                    t += colour(w2, 33) + colour(" != ", 32)
                    t += colour(w1, 41)
                else:
                    t += "%s: %s -> %s != %s\n" % (d, word, w2, w1)
                continue

            if col:
                t += colour(d, 35) + colour(": ", 32) + colour(w2, 33)
            else:
                t += "%s: %s" % (d, w2)

            if w1 != w2:
                if col: t += " " + colour(w1, 41)
                else:   t += " **%s**" % w1

            t += " "

        if len(t): print t.encode(enc)

    if not m: print
    print "Mismatches: %d" % n
    
##############################################################################

def doLexFile(sc, lexfile, enc, dialects, col):
    f = codecs.open(lexfile, 'r', enc)

    for s in f.readlines():
        s = s.rstrip()
            
        H = {}
        for d in dialects: H[d] = []

        for i, word in enumerate(s.split(insep)):
            if not fields or i in fields:
                words = sc.process(word, dialects)
                for d in dialects: H[d].append(words[d])
            else:
                for d in dialects: H[d].append(word)

        if sep:
            t = [ string.join(H[d], insep or " ") for d in dialects ]
            print (sep.join([s] + t)).encode(enc)
            continue

        if col:     print colour(">", 33) + s.encode(enc)
        elif not m: print ">: " + s.encode(enc)

        for d in dialects:
            t = string.join(H[d], insep or " ")

            if col:     print (colour(d, 33) + t).encode(enc)
            elif not m: print (d + ": " + t).encode(enc)
            else:       print t.encode(enc)

##############################################################################

opts = clopthandler(shortargs, longargs)
sep  = opts["-s", "--sep"]
enc  = opts["-e", "--enc"] or "utf-8"

scfile   = opts["-c", "--scfile"]
testfile = opts["-t", "--testfile"]
lexfile  = opts["-l", "--lexfile"]

if scfile is None: die(1, "No sound-change file specified!")
if scfile[-3:] != '.sc': scfile += '.sc'

if opts["-q", "--quiet"] is None: showBanner(banner, lexfile)

try: sc = SC(scfile, enc)
except scException, e:
    s = '%s' % e
    print s.encode(enc)
    sys.exit(0)

dialects = opts["-d", "--dialects"] or sc.dialects

for c in dialects:
    if c not in sc.dialects:
        die(1, "'%s' is not defined as a dialect in '%s'", c, scfile)

insep  = opts["-F", "--insep"]
fields = parsefields(opts["-f", "--field"]) or None

if sep: header = string.join(["in"] + list(dialects), sep)

# words come from command-line

if lexfile is None and testfile is None:
    if sep: print header
    for s in opts.A: processAll(sc, s, dialects, opts, sep = sep)
    sys.exit(0)

# we have a lexicon file or a test file

if sep: print header

col = opts["-C", "--colour" ] is not None
m   = opts["-m", "--minimal"] is not None

# do test file first

if testfile:
    doTestFile(sc, testfile, insep, col, m)
    sys.exit(0)

# we have a lexicon file

doLexFile(sc, lexfile, enc, dialects, col)

##############################################################################
