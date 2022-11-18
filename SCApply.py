# This file is part of Geoff's Sound Change Applier, version 0.8
# (August 2010). You can obtain the latest version of this program
# from http://gesc19764.pwp.blueyonder.co.uk/sca.html

from SCA import *

import sys, optparse, yaml, codecs, random, time

banner = "Geoff's Sound Change Applier, version 0.8 (August 2010)"
info1  = "You can obtain the latest version of this program"
info2  = "from http://gesc19764.pwp.blueyonder.co.uk/sca.html"

""" Still to do:

- deterministic 'random' numbers based on words
- documentation!!!
- notes about converting from older versions

New:

- maybe use csv class?
"""

##############################################################################

""" This is a class which does command-line based sound-changes. """

class SCApplier():
    """ The constructor. """
    def __init__(self):
        self.defs  = {}   # command-line variables with -D
        self.fout  = None # output file, if specified

    """ Do something according to the command-line arguments, which
    are stored in _OP_.
    """
    def go(self, OP):
        (opts, args) = OP.parse_args()

        self.opts = opts

        if opts.encoding is None: opts.encoding = "utf-8"

        S = SCA(self.defs, opts.encoding)
        S.readFromFile(opts.scfile)
        if opts.excfile: S.loadExceptions(opts.excfile)

        if opts.showdefs:
            S.showDefs()
            return

        if opts.fields is not None:
            opts.fields = makeNumList(opts.fields)

        if   opts.rules:  self.func = self.showRule
        elif opts.regexp: self.func = self.showRexp
        else:             self.func = None

        self.dialects = opts.dialects or S.dialects

        if opts.seed is not None:
            if opts.seed == 'time': random.seed()
            else: random.seed(opts.seed)
        else:
            S.setLastWord("")

        # display information if requested
        if not opts.quiet: self.printBanner(S)

        if opts.verbose: S.showRules()

        # actual processing starts here

        if self.opts.testfile: self.doTestFile(S)

        if self.opts.lexfile: self.doLexFile(S, self.opts.outfile)

        try:
            for word in args: self.process_word(S, word)
        except SCAException, e:
            print e.s

    """ Read lines from file _name_, split them into fields, and yield
    them together with the line number.
    """
    def readFile(self, name):
        f, n = codecs.open(name, "r", self.opts.encoding), 0
            
        for line in f.readlines():
            n += 1
            L = line[:-1].split(self.opts.insep)
                
            yield n, L

        f.close()

    """ Process a file which contains words. The file name is taken
    from the '-l' command-line argument.
    _S_: the SCA instance with which to process the words
    _outfile_: name of a file to write the output to (may be None); this
    comes from '-o'.
    """
    def doLexFile(self, S, outfile):
        fout, w = None, self.opts.width or 15

        if outfile is not None:
            fout = codecs.open(outfile, "w", self.opts.encoding)

            if fout is None:
                raise SCAException("Can't write to '%s'", outfile)

        for n, L in self.readFile(self.opts.lexfile):
            if self.opts.fields is None: words = L
            else:
                words = [ L[i] for i in self.opts.fields
                          if 0 <= i < len(L) ]

            if fout is None:
                for word in words: self.process_word(S, word)
                continue

            if n == 1 and self.opts.header:
                for d in self.dialects: L.append(d)
            else:
                for word in words:
                    H = S.process(word, self.dialects)
                    for d in self.dialects: L.append(H[d])

            if self.opts.sep is not None:
                s = self.opts.sep.join(L)
            else:
                s = "".join(["%-*s" % (w, t) for t in L])

            fout.write(s + "\n")

        if fout is not None: fout.close()

    """ Process a test file through _S_, whose name comes from '-t',
    and report any differences.
    """
    def doTestFile(self, S):
        self.opts.fields, first, incol, outcol = None, True, None, None

        for n, L in self.readFile(self.opts.testfile):
            if first:
                for i, s in enumerate(L):
                    if   s == 'out': outcol = i
                    elif s == 'in':  incol  = i
                    elif s not in S.dialects:
                        raise SCAException("Invalid column header " +
                                           "'%s' in testfile '%s'",
                                           s, self.opts.testfile)

                if incol is None:
                   raise SCAException("No input column header " +
                                      "in testfile '%s'",
                                      self.opts.testfile)

                header, first = L, False
                continue

            word = L[incol]

            label = "" if outcol is None else f" ({L[outcol]})"
            H = S.process(word, self.dialects)

            for i, d in enumerate(header):
                if i == outcol: continue
                if d == "in" or H[d] == L[i]: continue

                if self.opts.colour:
                    t = f"{cols(word, 35)} in {cols(d, 32)}"
                    t += f" at line {cols(n, 36)}"
                    t += cols(label, 34)
                    t += f": expected {cols(L[i], 33)}"
                    t += f"; got {cols(H[d], 31)}"
                else:
                    t  = "'%s' in '%s' %s: expected '%s', got '%s'" %\
                             (word, d, label, L[i], H[d])

                if i == outcol: continue

    """ Callback which handles definitions with '-D'. """
    def define(self, option, opt, value, parser, *args, **kwargs):
        i = value.find('=')

        if i < 0: self.defs[value] = None
        else:     self.defs[value[:i]] = value[i + 1:]

    """ Process _word_ through _S_ in all the relevant dialects,
    and print the details to the console if necessary.
    """
    def process_word(self, S, word):
        if not self.opts.minimal and self.opts.sep is None:
            print cols("> ", 43, self.opts.colour) + word

        H = S.process(word, self.dialects,
                      doassert = self.opts.doassert,
                      func = self.func)

        if self.opts.sep is not None:
            print self.opts.sep.join([H[d] for d in self.dialects])
            return

        if self.opts.minimal:
            print " ".join([H[d] for d in self.dialects])
            return

        for d in self.dialects:
            print cols(d, 43, self.opts.colour) + " " + H[d]

    """ Display a heading if necessary. """
    def showHeading(self, n, word):
        if self.opts.level <= n: return

        s = "#=-"[n] * 8
        s = f"{s} {word} {s}"

        if self.opts.level <= n: return

        print cols(s, 45, self.opts.colour)

    """ Callback for the '-r' option. """
    def showRule(self, *args): self.showCommon(True,  *args)

    """ Callback for the '-R' option. """
    def showRexp(self, *args): self.showCommon(False, *args)

    """ Common callback function, which shows the results of each rule
    as it is processed. See SCArule.process() for the arguments.
    """
    def showCommon(self, b, rule, d, n, word, w, p):
        if d is None: self.showHeading(n, word); return

        if word == w and not self.opts.all: return

        s = ""

        if self.opts.showlines: s += "[%4d] " % rule.line

        if self.opts.colour:
            s += f"{cols(d, 32)} "

            if n == 2: c = 33 # exception
            elif self.opts.all and word == w: c = 0 # no change
            elif p:    c = 45 # persistent
            else:      c = 44 # something changed

            s += cols(w, c) + " " * (20 - len(w))
        else:
            s += "%s: %-20s" % (d, f"{w} *") if n == 2 else "%s: %-20s" % (d, w)
        s += rule.getShowText(b, self.opts.colour)

        if d is None: self.showHeading(n, word)
        print s.strip().encode(self.opts.encoding)

    """ Print the starting banner and definition counts.
    _S_: where to ge the counts from.
    """
    def printBanner(self, S):
        n = len(banner)
        s1 = "*" * n
        s2 = " " * n

        L = [s1, s2, banner, info1.center(n), info2.center(n), s2, s1]

        for s in L:
            sys.stderr.write(cols(f"* {s}" + " *\n", 44, self.opts.colour))

        if self.opts.lexfile:
            sys.stderr.write("\nProcessing %s with %s.\n" % \
                      (self.opts.lexfile, self.opts.scfile))
        elif self.opts.testfile:
            sys.stderr.write("\nTesting %s with %s.\n" % \
                      (self.opts.testfile, self.opts.scfile))
        else:
            sys.stderr.write("\nUsing " + self.opts.scfile + ".\n")

        sys.stderr.write(S.getCounts() + "\n")

##############################################################################

Y  = yaml.load(file("SCAparams.yaml", "r"))
OP = optparse.OptionParser(version = Y['version'])
S  = SCApplier()

for c in Y:
    if len(c) > 1: continue
    H = Y[c]

    c = '-' + c

    dest     = H['long']
    longname = "--" + dest
    helptext = H['help']
    default  = H.get('default', None)
    
    t = H.get('type', 'string')

    if t == 'bool_true':
        OP.add_option(c, longname, action = 'store_true', default = False,
                      help = helptext, dest = dest)
    elif t == 'callback':
        OP.add_option(c, longname, action = 'callback', type = H['argtype'],
                      callback = getattr(S, H['func']), help = helptext)
    else:
        OP.add_option(c, longname, type = t,
                      dest = dest, default = default, help = helptext)

try:
    S.go(OP)
except SCAException, e:
    print e.s

##############################################################################
