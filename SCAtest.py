# This file is part of Geoff's Sound Change Applier, version 0.8
# (August 2010). You can obtain the latest version of this program
# from http://gesc19764.pwp.blueyonder.co.uk/sca.html

# This is a test program for the SCA class. It uses SCAtest.yaml for
# its definitions.

import yaml, sys, traceback

from SCA import *

debug, verbose, colour, tests = False, False, True, []

for arg in sys.argv[1:]:
    if   arg[:2] == '-c': colour  = False
    elif arg[:2] == '-v': verbose = True
    elif arg[:2] == '-d': debug   = True
    else:                 tests   = makeNumList(arg)

S = SCA()

Y = yaml.load(file("SCAtest.yaml", "r"))

good, bad, rules, L, names = 0, 0, 0, [], set([])

try:
    for s in [ "cat", "list", "string", "feature" ]:
        for i, H in enumerate(Y[s + "s"]):
            S.addDef(s, H["name"], H["def"])
except SCAException, e:
    print cols("Caught an SCA exception in definitions!", 41)
    print cols(cols(e.s, 33), 41)
    traceback.print_exc()
    sys.exit(1)
except Exception, e:
    print cols("Caught an exception in definitions!", 41)
    print cols(cols(str(e), 33), 41)
    traceback.print_exc()
    sys.exit(1)

try:
    for i, H in enumerate(Y["rules"]):
        if len(tests) > 0 and i not in tests: continue

        name = H.get("name", None)

        if name is None:
            raise SCAException("Test %d has no name", i)

        if name in names:
            raise SCAException("Duplicate test name %d '%s'", (i, name))

        if verbose:
            print cols("=" * 20 + " " + name, 37)
            print "%4s: %s" % (cols(i, 37), cols(H["rule"], 35))

        R = SCARule(S, "test", i, "* " + H["rule"], None, verbose = debug)

        S.activegroup.addRule(R)
        rules += 1

        for old, new in H["test"]:
            ret, t = R.apply('', old, None, debug)

            if verbose:
                print "  %s -> %d %s: " % (cols(old, 33), ret, cols(new, 36)),

            if t == new:
                if verbose: print cols("OK!", 32)
                good += 1
            else:
                if verbose:
                    print "%s: got '%s'" % (cols("FAIL", 31), cols(t, 35))
                    print cols("     " + R.getRexp(), 31)

                L.append((i, name, old, new, t, R.getRexp()))
                bad += 1

    print cols(cols("%d tests completed for %d rules" % \
                    (good + bad, rules), 37), 44)
except SCAException, e:
    print cols(cols("Caught an SCA exception in test %d '%s'!" % \
                    (i, name), 33), 41)
    print cols(cols(H["rule"], 33), 41)
    print cols(cols(e.s, 33), 41)
    traceback.print_exc()
except Exception, e:
    print cols(cols("Caught an exception in test %d '%s'!" % \
                    (i, name), 37), 41)
    print cols("%s" % H["rule"], 41)
    traceback.print_exc()

print "%s good, %s bad" % (cols(good, 32), cols(bad, 31))

if not verbose:
    for i, name, old, new, t, r in L:
        print "%4s: %s: %s %s -> %s (%s)" % \
              (cols(i, 37), cols(name, 37), cols(r, 31), cols(old, 33),
               cols(new, 36), cols(t, 32))
