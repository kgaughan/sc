Geoff's Sound Change Applier
============================

Last update: 31 August 2010 (version 0.8)

Contents
--------

-   [About SCA](#about)
-   [Rules and terminology](#rules)
-   [Higher-level processing](#hlp)
-   [Command-line options](#clopts)
-   [Converting from older versions](#conv)
-   [Sample rules](#sample)

About SCA
---------

Geoff's Sound Change Applier, **SCA** hereafter, is a program which
applies rule-based transformations to strings of Unicode text. It is
written in [Python](http://www.python.org) and uses configuration files
in [YAML](http://yaml.org/), so you'll need to install Python (SCA is
known to work with version 2.6, but probably won't with 3.x) and
[PyYAML](pyyaml.org) to be able to use it.

SCA was originally written as an aid for linguists and conlangers to
simulate the effects of the Neo-grammarian concept of sound-change and
is accordingly oriented towards this use, although it should be usable
for any similar non-linguistic task. You can, for example, very easily
write [L-systems](http://en.wikipedia.org/wiki/L-system) in it. It was
originally based on [a C program written by Mark
Rosenfelder](http://www.zompist.com/sounds.htm), which is fine for what
it does, but I needed something more powerful for my porpoises, which
frequently require one word to be converted into several descendants
simultaneously. I recommend reading the documentation for his program
anyway, since although it works somewhat differently from mine, many of
the underlying concepts and principles are the same.

For version 0.8, SCA has been completely redesigned and rewritten. It is
not completely compatible with earlier versions; a section in this file
explains what to do to convert .sc files which used to work.

### Getting SCA

All of the necessary files are stored in this repository:

-   **SCAdefs.py SCAitem.py SCArule.py SCA.py SCApply.py**: The Python
    implementation.
-   **SCAchars.yaml SCAdirparams.yaml SCAparams.yaml**: The YAML
    configuration files. Don't edit these unless you are absolutely sure
    you have a good reason for doing so.
-   **SCAtest.py SCAtest.yaml**: a test suite. You can safely ignore
    this, but you're still welcome to add tests to it.
-   **README.md**: a copy of this file.
-   **spanish.sca**: sample file with very approximate sound changes
    from Latin to Spanish. It is most definitely *not* guaranteed to be
    authoritative!
-   **ipa.sca**: some definitions for use with IPA symbols.

### Licensing and re-use

I can't guarantee that SCA will be suitable for your requirements, but
if you use it and find it helpful, I'd love to know. I'd also be
interested to hear about any suggestions you have for future
improvements and any bugs which you may have found.

You may do what you like with SCA, free of charge, including using its
code in something of your own; if you want to know how to do this, and
can't figure it out from the code, just ask me for the details. I only
ask that you credit me and link to this page if you use SCA for anything
you publish, whether software or output: share and enjoy, don't steal
credit for something you didn't create. Something like "Output generated
by [Geoff's SCA](http://gesc19764.pwp.blueyonder.co.uk/sca.html)" will
do fine.

Rules and terminology
---------------------

SCA's behaviour is specified by a sequence of **rules**, which are
typically stored in one or more text files and executed with the
**SCApply.py** script. If you want to try the following examples out for
yourself, type the rule into a file, save the file as "foo.sca", and run
the script as follows:

    python SCApply.py -q -cfoo <WORD>

where `WORD` is the example word; it can actually be several words, if
you're feeling adventurous.

### Basic replacements

The most basic rule simply replaces all occurrences of one piece of text
with another, for example:

    * a x _   ! banana -> bxnxnx

This rule consists of five elements, which are separated by white space:

-   A **dialect specifier**. Ignore this for now.
-   The text which needs to be changed. This is referred to as `BEFORE`
    hereafter.
-   What `BEFORE` should be changed to; this is `AFTER`.
-   The **environment**. This must contain an underscore; the text
    before this underscore is referred to as `PRE`, and the text after
    it is called `POST`. If both `PRE` and `POST` are empty, it means
    "everywhere".
-   A **comment**. This consists of the exclamation mark and everything
    which follows it, and is ignored. Comments in the example rules in
    this document show what the effect of the rule will be.

Comments are optional; the other parts are mandatory. `BEFORE` and
`AFTER` are together known as the **change** (better, perhaps,
**transformation**, but that's longer to type).

`PRE` and `POST` may be used to restrict the change to occur before or
after, or between, specific text; this models **conditioned**
sound-changes in historical linguistics:

    * a x b_   ! banana -> bxnana
    * a x _n   ! banana -> bxnxna
    * a x n_n  ! banana -> banxna

Note, however, the following:

    * n x a_a   ! banana -> baxana

This does not give `baxaxa` - why? The answer is closely related to the
**banana problem**, which asks, "how many occurrences of `ana` are there
in `banana`? The problem is that there are either one or two, depending
on whether you count overlapping occurrences or not. By default, SCA
only considers nonoverlapping occurrences, but you can append a **flag**
to a rule to make it consider overlapping ones as well:

    * n x a_a B  ! banana -> baxaxa

Anything which follows the environment is ocnsidered to be a flag. Some
other ones are `F` (for "first"), which performs the replacement once
only starting from the beginning, and `L` (for "last"), which does the
same from the end:

    * a x _ F  ! banana -> bxnana
    * a x _ L  ! banana -> bananx

There is also `R`, which does the same as `B` but starting from the end.

NOTE: Use at most one of `BRFL`. The results of combining them are not
guaranteed.

### Quantifiers

SCA supports the regular expression metacharacters `. ? + * |`, so you
can write rules like:

    * b|n x _  ! banana -> xaxaxa
    * nc? x _  ! bananca -> baxaxa
    * na* x _  ! bananaanta -> baxxxta
    * na+ x _  ! bananaanta -> baxxnta
    * b.n x _  ! bananabendy -> xanaxdy

`BEFORE` in these rules means respectively:

-   `b` or `n`
-   `n`, optionally followed by a `c`
-   `n`, optionally followed by one or more `a`'s
-   `n`, followed by one or more `a`'s
-   `b`, followed by anything, followed by `a`

Generally speaking, though, it's better to avoid such explicit regular
expressions in SCA; there are almost always better ways to specify what
you want.

If you want to use a character with special meaning as itself, precede
it with a backslash; this includes the backslash character itself:

    * \+ plus _ ! 3+3 -> 3plus3
    * \\ /  _ ! path\to\file -> path/to/file

### Categories

Suppose you want to replace all vowels in a word with `x`. One way to do
this is with the first rule:

    * a x _

repeated five times, with `a` replaced successively by `e i o u`. But
this is clearly inefficient; a better rule is:

    * a|e|i|o|u x _

Still better, though, is to define a **category**:

    vowel = aeiou
    * <vowel> x _  ! facetious -> fxcxtxxxs

The first line defines the category `vowel` to consist of the letters
**aeiou**; the second refers to it in `BEFORE`.

A category is an ordered list, so if you have categories in both
`BEFORE` and `AFTER`, SCA will replace a character in the first category
with the corresponding one in the second:

    ustop = ptc
    vstop = bdg
    * <ustop> <vstop> _  ! reaction -> reagdion

You can also use categories in `PRE` and `POST`, so you can model
Welsh-style intervocalic lenition of voiceless stops with:

    vowel = aeiou
    ustop = ptc
    vstop = bdg
    * <ustop> <vstop> <vowel>_<vowel>  ! tecos -> tegos

A category name should really consist only of letters and digits, must
not start with a digit, and should not be all in uppercase. (Personally,
I'd disallow digits completely.)

You can't use a category in `AFTER` to replace simple text in `BEFORE`,
because there is no meaningful way to decide which value from the
category to use, so you can't do this:

    * h F _ ! ERROR!

### More about categories

A category name can also be a single uppercase character, in which case
the angle brackets are not needed to refer to it:

    C = bcdfghjklmnpqrstvwxyz
    V = aeiou
    * C x V_V ! ambitious -> ambixious

Categories can be extended, combined, and reduced in several ways. For
example, in definitions:

    cat1 = abc def  ! cat1 = "abcdef"
    cat2 = cat1 ghi ! cat2 = "abcdefghi"
    cat3 = ca t1    ! cat3 = "cat1"
    A    = abc Def  ! A    = "abcDef"
    B    = xyz      ! B    = "xyz"
    C    = A g h i  ! C    = "abcDefghi"
    D    = jkl      ! not allowed; "D" has previously been used as a symbol.
    E    = AB       ! E    = "AB"; don't do this either.
    F    = A B      ! F    = "abcxyz"; this is the correct way to do it.

And in references:

    cat = abcdef
    dog = ghijkl

    <cat>         ! "abcdef", of course
    <^cat>        ! Complementation; anything but "abcdef"
    <cat+ghi>     ! Augmentation; "abcdefghi"
    <cat-ace>     ! Subtraction; "bdf"
    <+ghi>        ! One-off reference; "ghi"
    <-ghi>        ! One-off complement; anything other than "ghi"
    <cat,dog>     ! Combination; "abcdefghijkl"
    <cat,dog+xyz> ! Combination; "abcdefghijklxyz"
    <cat,dog-aei> ! Combination; "bcdfghjkl"

It is better to use these for one-offs only and define separate
categories if you need to use them a lot.

In general, a string of letters in a category reference will be treated
as the category definition if there is one, otherwise the letters
themselves. Note, however, that if all contiguous letters in a reference
are uppercase, they will be treated as categories; thus `<AB>` is the
same as `<A+B>`.

SCA tries to be sensible when one category replaces another and there
are different numbers of characters in the two categories, or if there
are duplicate characters. If the category in `BEFORE` is longer, the
extra characters are deleted; if the one in `AFTER` is longer, the extra
charactres are simply ignored:

    * <+abcde>  <+xyz>    _ ! debacle -> yxzl
    * <+abc>    <+vwxyz>  _ ! debacle -> dewvxle

Duplicates in `AFTER` should not be surprising; duplicates in `BEFORE`
ignore every occurrence except the first:

    * <+abcde>  <+xxyyz>  _ ! debacle -> yzxxylz
    * <+abbcde> <+xxyyzz> _ ! debacle -> zzxxylz

It's legal to use quantifiers with categories, thus, to remove sequences
of `x` followed by one or more vowels, you'd do this:

    * x<vowel>+ 0 _

Zeros in a category in `AFTER` will delete the corresponding characters
in `BEFORE`:

    * <+abcde>  <+x0y0z>  _ ! debacle -> zxylz

Finally, note this rather silly situation:

    T = ptk
    V = aeiou
    * <TV> <VT> _

The rule is equivalent to:

    * <+ptkaeiou> <aeiouptk> _

which probably won't do what you want.

### Features

Features are an alternative way of looking at category replacements.
They're an attempt to satisfy those who prefer the lower-level sort of
sound-change rule which looks like this:

    * [-voice] [+voice] V_V ! ata -> ada

A feature is defined as a pair of category-like definitions separated by
a pipe. The first part of the pair specifies the characters which do not
have the feature, and the second part specifies those which do, so that
the meaning is "adding the feature to each character in the first part
produces the corresponding character in the second part". There must be
the same number of characters in each part. For example, `voice` could
be defined as one of the following:

    feature voice ustop ufric | vstop vfric
    ptk f s h | b d g vz G

Features can't be defined in terms of other features, but they can be
combined:

    feature fric ustop vstop | ufric vfric ! define feature "fric"
    [-voice,-fric] [+voice,+fric] V_V      ! kata -> kaza

### Indexes, positions, and zero

The following definitions are assumed hereafter.

    T = ptk
    D = bdg
    F = fÎ¸x
    N = mnÅ
    V = aeiou
    L = lr
    stop = T D

In a rule like:

    * F Th _ ! fotografy -> photography

SCA is clever enough to know that `T` and `F` are both in the same
position in their parts, so an `F` should be replaced with a `T`. The
reverse will also work, so:

    * Th F _ ! photography -> fotografy

However, this (hello, Sally Caves!) won't:

    * F hT _ ! ERROR!

because there is nothing corresponding to the `T`. However, you can do
this instead:

    * F h<1T> _ ! fotografy -> hpotograhpy

Internally, `BEFORE` and `AFTER` are converted to a sequence of
**items**; a category makes up a single item, as does any contiguous
string of ordinary characters and regexp metacharacters. In `AFTER` in
this rule, `<1T>` means "replace the first item in `BEFORE` with the
corresponding `T`"; this is called a **category mapping**. Note that the
angle brackets are mandatory here, regardless of the name of the
category.

Digits can be used in `AFTER` to refer to items in `BEFORE`, so you can
make two characters change places (**metathesis**) with:

    * VL 21 _ ! tort -> trot

The digit `0` (zero) has the special meaning of "nothing". So you can
get rid of characters you don't like by replacing them with zero:

    * F 0 _ ! fusty -> uty

A more complicated example, which deletes anything between an `N` and a
`T`, is:

    * . 0 N_T ! nutmeg -> ntmg

This can also be written:

    * N.T 13 _ ! nutmeg -> ntmg

Our problematic rule earlier can also be fixed with a zero to pad the
rule out, although this is not recommended:

    * 0F hT _ ! fotografy -> hpotograhpy

In general, if you have several ways of expressing the same rule, the
choice depends on how you view the rule. For example, both the following
do the same thing:

    * etymology entomology _
    * ty        nto       e_mology

but one views the change as replacing one complete string with another,
while the other considers only the parts which actually change.

If you have zero on its own in `BEFORE`, you can create characters out
of nothing (**epenthesis**):

    * 0 p m_r ! amra -> ampra

This is more useful with [blends](blend), with which it can be
generalised.

### Strings and lists

A **string** is a sequence of characters which you would like to use
more than once. For example, if you want to censor the string 'xenu'
differently in different contexts, you can do this:

    string foo xenu     ! define string 'foo'
    * $foo$ xxxx _\.net ! www.xenu.net -> www.xxxx.net
    * $foo$ yyyy _      ! "his name was xenu" -> "his name was yyyy"

A **list** is like a category, except that it is made up of strings
rather than single characters:

    list dips   ei,ai,oi,eu,au,ou  ! define list 'dips'
    list single i,e,e,u,o,o        ! define list 'single'
    * ~dips~ ~single~ _            ! reitainous -> ritenos

You can interpolate strings in lists, and replace lists and categories
with each other:

    list dips   ei,ai,oi,eu,au,ou
    foo = uvwxyz
    * ~dips~ <foo> _ ! daireitous -> dvrutzs
    * <foo> ~dips~ _ ! vexedly -> aieoiedlau

Note, however, that this won't do what you might expect:

    list dips   ei,ai,oi,eu,au,ou
    * ~dips~ <+ieeoou> _ ! daireitous -> derits

This is because `<ieeoou>` is a category, not a list, and it ends up as
`ieou`.

### Referring to BEFORE, PRE, and POST

Suppose you want to reduce a sequence of two identical characters to
one. Within SCA, the way to do this is to regard it as removing a
character if it appears after itself, so we need a way of specifing that
`PRE` is to be equal to `BEFORE`. The percent sign is interpreted in SCA
as meaning `BEFORE` when it in `PRE` or `POST`:

    * a 0 %_ ! bazaar -> bazar
    * a 0 _% ! bazaar -> bazar, exactly the same

This will also work with strings and, more usefully, lists:

    string foo xyz
    list dips ei,ai,oi,eu,au,ou
    * $foo$  0 %_ ! xyzxyz -> xyz
    * ~dips~ 0 %_ ! raiain -> rain

The signs `<` and `>` can be used by themselves in `AFTER` to represent
`PRE` and `POST` respectively; this models **complete assimilation**:

    * N > _D ! android -> addroid
    * D < N_ ! android -> annroid

And you can also use `<` in `POST`; thus to delete something which
appears between two identical vowels:

    * N 0 V_< ! canal -> caal

You can have other things in `PRE` and `POST` alongside the percent
sign, although this is not yet guaranteed to work:

    * a 0 _n% ! banana -> bnna

### Anchors

The hash character in `PRE` means "the beginning of the text", and in
`POST` it means "the end of the text". So you can remove a single final
vowel with:

    * V 0 _# ! racine -> racin

or several with:

    * V+ 0 _# ! superbee -> superb

Similarly, to put an `h` before an initial vowel:

    * 0 h #_V ! umour -> humour

Quite often, you need to indicate "initially or after a consonant"; this
works as you might expect:

    * h 0 #|<cons>_ ! heather -> eater

### Blends

Blends are probably the trickiest part of SCA to understand, which is
why they have been left to last.

A blend is a special type of category replacement in which the category
and the index of the replacement character in the category come from
different places, rather than taking them both from `AFTER`. It is
specified as `{cat:pos}`, where **cat** specifies the category and `pos`
the position. For example, in:

    * N {1:>1} _T ! anpa -> ampa

the category comes from `BEFORE` and the position from `POST`; the
effect is that the item in `AFTER` remains a nasal, but shifts position.
In linguistic terms, this is **regressive assimilation** of the nasal to
the following stop. If you switch the two parts of the blend, like this:

    * N {>1:1} _T ! anpa -> atpa

the position stays the same, but the category changes instead. This is
almost the same as this normal category replacement:

    * N T _T ! anpa -> atpa

except that the replacement category comes from `POST` rather than being
explicitly specified.

`1` means "the first item in `BEFORE`", and `>1` means "the first item
in `POST`". Similarly, `<1` means "the first item in `PRE`", and can be
used to indicate **progressive** assimilation:

    * N {1:<1} _T ! anpa -> anta
    * N {<1:1} _T ! anpa -> anma

The indexes - `1` in all of these examples - can be omitted, in which
case the item from which the category or position is taken is the
corresponding item in the appropriate part. So, these four examples
could also be written:

    * NT {:2}2 _ ! anpa -> ampa
    * NT {2:}2 _ ! anpa -> atpa
    * NT 1{:1} _ ! anpa -> anta
    * NT 1{1:} _ ! anpa -> anma

where the unspecified category indexes are taken to be 1 in the first
two and 2 in the others.

Blends can also model **epenthesis**, with zero in `BEFORE`; you need
either to have both `PRE` and `POST` in the blend:

    * 0 {>:<} N_T ! amta -> ampta
    * 0 {<:>} N_T ! amta -> amnta

or an explicit category in the category part:

    * 0 {T:<} N_L ! anra -> antra
    * 0 {T:>} L_N ! arna -> artna

Alternatively, if you prefer to keep your environments clean, you can do
these instead:

    * NL {T:1}   _ ! anra -> antra
    * LN {T:2}   _ ! arna -> artna
    * NT 1{2:1}2 _ ! amta -> ampta
    * NT 1{1:2}2 _ ! amta -> amnta

### When all else fails - temporary environments

Sometimes you just can't get a single rule to do what you want to; in
this case, you'll probably need two or more rules and a bit of fiddling.
For example, say you want to delete a `h` between two vowels, but not if
the first is `a` and the second `u`. With a single rule, this is almost
impossible. Instead, you can set up a temporary environment with an
otherwise unused character:

    * 0  ; Vh_V B ! tentatively mark each 'h'; note the banana flag
    * ;  0 ah_u   ! remove the marker if necessary
    * h; 0 _      ! and get rid of the remaining 'h's.

Quite often, you'll need a rule which removes stray characters after
this kind of thing:

    * ; 0 _ 

Higher-level processing
-----------------------

SCA has a number of ways to consider rules as more than just isolated
items in a sequence. The principal mechanisms for this are
**directives** and **comments**.

### Comments

Actually, comments don't do anything; they're merely a way for you to
annotate your files without interfering with SCA.

A comment may be specified in two ways. We've already seen the
exclamation mark, which turns everything after itself into a comment if
it's not at the start of a line. If you want an entire line to be a
comment, put a hash character at the start. So:

    * foo bar _ ! this is a comment
    # so is this
    !but this isn't - it's a directive and will cause an error
    ! nor is this
    * foo bar _ # and nor is this; it looks like an anchor or a flag

### Directives

A line which starts with an exclamation mark is a directive; it's an
instruction to SCA to do something other than define a rule, category,
or whatever. For example:

-   `!end` tells SCA not to read any more input. This takes precedence
    over aanything else.
-   `!skip` tells SCA to ignore all further input lines until further
    notice.
-   `!noskip` undoes all preceding `!skip`s, which do not nest.

These are provided for convenience and not as part of a **cpp**-like
preprocessor; I really hope nobody's files get that complicated anyway.

Mnay directives take parameters, which are given as `!param=value`; some
parameters have no value and are given as just **param**. For example:

-   `!include file=FILE` will read in the contents of `FILE` before
    proceeding with the current file. You will be warned about recursive
    includes, so don't try it.

Other directives will be introduced as appropriate.

You can specify that the value of a parameter may be [supplied on the
command-line](#def) (q.v.). Two directives which can only work this way
are:

-   `!skipif COND`: like `!skip`, but only if `COND` is defined on the
    command-line with `-DCOND`
-   `!skipunless COND`: similarly, but only if it is not defined.

### Groups and randomisation

Rules can be **grouped** into larger entities with the `!group`
directive; `!endgroup` signals the end of the group. By itself this
isn't very useful, but with the appropriate parameters you can add a bit
of non-determinism to your processing:

-   `times=N` will execute the group exactly `N` times.
-   `shuffle` will randomly reorder the rules in the group before
    applying them, once per iteration.
-   `max=N` will process the first `N` rules in the group; this is
    useful in conjunction with `shuffle`.
-   `pick=N` is equivalent to `shuffle max=N`, and will apply `N` random
    rules out of the group.
-   `prob=N` will execute the entire group only if a random number
    between 0 and 100 is less than `N`.
-   `ruleprob=N` is similar, but the probability applies to each
    individual rule within the group.
-   `reduce=N` can be used to decrease the values of `prob` and
    `ruleprob` after each iteration; for example, `reduce=50` will halve
    them each time.
-   `seed=string` will seed the random numbers with `string`. If
    `string` equals `time`, the system clock will be used instead, which
    should ensure that the random numbers are unpredictable. If `string`
    is `word`, the default settings are used (see below).

You can apply random probabilities to individual rules by expressing the
probability as a percentage flag:

    * x 0 _ 50 ! get rid of the x's half of the time

And you can select random values from categories:

    * x <@vowel> _ ! change x's to random vowels

By default, the random numbers are seeded each time with the next word
to be processed, or with the recently-processed word for the group-based
parameters. This effectively means that rules with percentages will
affect the some words each time, which is hopefully a good simuation of
incomplete sound change.

#### Persistence

A special group consists of the **persistent** rules, which are
specified with the `P` flag. These rules are all applied, in the order
in which they are defined, after each non-persistent rule; for example:

    * x 0 _ P ! ensure that we never have any x's

### Dialects

A **dialect** is a path through the sequence of rules. Its name derives,
of course, from SCA's original application in simulating historical
linguistic development.

Dialects are identified by single letters or digits; by default you get
the one dialect `A`. All dialects to which your file applies must be
specified at the top of the file with the `!dialect` directive; thus
`!dialect AB C D` declares that you have four dialects called `A B C D`.
You can then declare that a rule applies to certain dialects only, thus:

    A...  ~ai,au~  <+EO>   _   ! dialect 'A' collapses diphthongs
    .B..  <ustop>  <vstop> V_V ! dialect 'B' does lenition
    ..C.  V        <@V>        ! dialect 'C' mangles vowels

The dots aren't necessary, but are convenient for lining up the text
neatly.

To save you having to type out the same dialect specifier in front of
several lines in succession, you can use the `!dirprefix` directive. The
value of its `dialects` parameter is prepended to each line:

    !dirprefix dialects=A
    # some rules for dialect 'A'
    !dirprefix dialects=B
    # some rules for dialect 'B'
    !dirprefix dialects=
    # now need actual dialect specs again
    AB foo bar baz_quux

### Exceptions

Occasionally you want a rule to ignore a specific word. This is done in
SCA through the mechanism of **exceptions**, which should not be
confused with the exceptions which programming languages throw when
something goes wrong.

To specify an exception to a rule, you need to do two things: identify
the rule, and say which combinations of dialects and words it doesn't
apply to. For example:

    !exception rule=FOO words=sanctus dialects=ABC
    *  c   0   n_t    _   @FOO

Here the `@FOO` flag gives the name `FOO` to the rule, and the
`!exception` directive says that in dialects `A B C` the word `sanctus`
wil be left alone.

As well as specifying exceptions in the file, you can put then in a file
of their own called `FILE`, which can be read in with the
`!exceptfile file=FILE` directive. This file must be in the following
format for each combination of rule and dialect:

    @RULE dialects
    words words words
    words words
    words

### Referring to previous rules and parts

If the backquote character `` ` `` appears in `BEFORE`, `AFTER`, or the
environment, the part is taken from the previous rule:

    A..  s   z   V_V   ! voicing
    .B.  `   h   `     ! lenition
    ..C  `   t   `     ! rhotacism

Equivalently, you can name the first rule and refer to it explicitly:

    A..  s     z V_V   @FOO
    .B.  `@FOO h `@FOO
    ..C  `@FOO t `@FOO

You can also name specific changes and environments, and use them later:

    change lenition     <ustop> <vstop>
    env    intervocalic V_V

    .B. `lenition `intervocalic

Note that the first definition here defines both `BEFORE` and `AFTER`;
there isn't a lot of point defining just one.

### Headings

A heading is a comment which is echoed back to the user if requested.
There are three levels of headings:

    !heading Top-level processing
    !subheading not so important stuff
    !subsubheading incidentals

For displaying headings in the output, see the `-L` [command-line
option](#clopts).

### Assertions

**Assertions** allow you to test whether a rule gives the output you
expect. By default they are ignored; you can tell SCA to take notice of
them with the `-A` [command-line option](#clopts).

You can specify an assertion with the `!assert` directive, which applies
to the most recently-defined rule:

    A t d a_e
    !assert dialect=A word=ate result=ade
    !assert dialect=B word=rate result=rate

The parameters are hopefully self-explanatory. If an assertion fails,
i.e. if applying the rule to `word` does not give `result` in `dialect`,
SCA will warn and exit.

### L-systems

Because SCA does list replacements in parallel, lists are ideal for
implementing the rules of an L-system. Here, for example, is how to
produce ten generations of Lindenmayer's original L-system:

    list predecessor a,b
    list successor   ab,a

    !group times=10
    L ~predecessor~ ~successor~ _
    !endgroup

No doubt, SCA could also specify a workable implementation of [John
Horton Conway's Game of
Life](http://en.wikipedia.org/wiki/Conway's_Game_of_Life). This is left
as an exercise for the reader.

Command-line options
--------------------

We've seen some command-line options already; here's the complete list.
Every argument has a short form, which is a single letter, and a long
form, which is one or more words; the short form is preceded by a
hyphen, and the long one by two:

-   `-X` or `--option` simply turns option `X` on;
-   `-Xvalue`, `-X value`, or `--option=value` supplies `value` with the
    option.

All of the options which SCA understands are specified in the file
`SCAparams.yaml`, so you can change them if you really need to.

### Miscellaneous options

-   `-cFILE` or `--scfile=FILE`: tell SCA which sound-change file to
    use. Note that this option is actually mandatory. If `FILE` does not
    end in `.sca`, this suffix will be appended automatically.
-   `-xFILE` or `--excfile=FILE`: load [exceptions](#exc) from `FILE`.
    This has the same effect as the `!exceptfile` directive at the start
    of the sound-change file.
-   `-i` or `--showdefs`: show everything which is defined and exit.
-   `-dDIALECTS` or `--dialects=DIALECTS`: process the words through
    `DIALECTS`. By default, all defined dialects are used.
-   `-eENC` or `--encoding=ENC`: use encoding `ENC` for input and
    output. The default is `utf-8`.
-   `-SSTRING` or `--seed=STRING`: set the random number seed to
    `STRING`; this is the same as the `!seed` directive.
-   `-A` or `--doassert`: run in [assertion mode](#assert).

### Definitions

A **definition** is a name-value pair which can be passed to SCA and
referred to in the parameter list of a directive. A definition is
specified with `-DNAME=VALUE` or`-define=NAME=VALUE`; the value may be
absent, in which case the equals sign is not needed and SCA is only
interested in whether `NAME` is defined.

You can refer to the definition with `&NAME:DEFAULT`; it is not wise not
to supply a default. For example:

    !group times=&times:5
    ... rules ...
    !endgroup

This will process the group five times by default, but you can specify a
different number of iterations with `-Dtimes=42`.

### Output to the screen

By default, SCA will print its output to the screen preceded by a banner
and some information about how many things are defined. Each input word
is preceded by "\>" followed by the outcome in each dialect on the
following lines. The following options affect the style of this display:

-   `-q` or `--quiet`: don't show the banner or counts.
-   `-v` or `--verbose`: show each rule as it's compiled.
-   `-m` or `--minimal`: just show the output words; this overrides
    everything below.
-   `-r` or `--rules`: display each rule which changes the word as text.
-   `-R` or `--regexp`: display each rule which changes the word as a
    regular expression; this is useful to see what's happening behind
    the scenes.
-   `-a` or `--all`: when used with `-r` or `-R`, shows all rules
    whether they make a change or not.
-   `-C` or `--colour`: add colour to the output; this requires an
    ANSI-compatible terminal.
-   `-n` or `--showlines`: show the line number on which the rule was
    defined.
-   `-LN` or `--level=N`: when used with `-r` or `-R`, displays
    headings, plus subheadings if `N` is 1 or greater, and
    subsubheadings if it is 2 or greater.

### Input files

SCA can read words from a file and process them in hopefully useful
ways.

The file is specified with `-lFILE` or `--lexfile=FILE`, as in Mark R's
program. If no other options are given, SCA will split each line in
`FILE` on whitespace and process every one of the resulting words. The
`-FSEP` or `--insep=SEP` option specifies an alternative separator, such
as a comma for `.csv` files.

If you don't want to process all words on a line, use the `-fFIELDS` or
`--fields=FIELDS` option. Here `FIELDS` is a comma-separated list of
numbers and ranges, for example `1,3-5` for fields 1 3 4 5, or `2` for
just one field. Note that the numbering starts at zero.

#### Test files

The `-tFILE` or `--testfile=FILE` option is especially interesting. It
expects an input file in a strict format, in which the first line is
treated as a header; one field in the header must contain the word `in`,
and each of the others must specify a dialect such as `A`; optionally,
one field may contain `out`. On each subsequent line, the word in the
field headed `in` is processed in each of the dialects specified in the
other fields in the header, and the results are compared to the
corresponding fields in the line; all differences are reported, with the
test in the `out` field (if present) output to facilitate
identification.

For example, if you're investigating Romance diachronics, you might use
a test file like this:

    in     out   P     E     F     I
    Ãºnus   one   um    uno   un    uno
    duÃ³    two   dois  dos   deux  due
    trÃ©s   three tres  tres  trois tre

### Output files

By default, the output from processing an input file goes to the screen.
There is a little magic built into SCA to send it to a file instead.

You can specify the output file name with `-oFILE` or `--outfile=FILE`.
By default the output is written in fixed-width columns of width 15; you
can change the width with `-wN` or `--width=N`, or supply an output
separator `C` with `-sC` or `--sep-C`.

What now happens is that each input line is written to the output, and
for each field specified with `-f` (all fields by default), the results
of processing the word in that field through the specified dialects are
appended to the input line. If you supply the `-H` or `--header` option,
the first line in the input file is treated as a header and is not
processed; the extra columns are identified with the respective
dialects. Obviously, you won't want too many input words on each line
when doing this.

Converting from older versions
------------------------------

If you have a `.sc` file from version 0.6 of the older SCA, you can
convert it to a `.sca` file which will work with version 0.8 with the
help of the following.

### Now directives

The following features should be convered to directives:

-   `#: #:: #:::` -\> `!heading !subheading !subsubheading`
-   `SKIP NOSKIP END` -\> `!skip !noskip !end`
-   `SKIP IF COND` -\> `!skipif cond=COND`
-   `SKIP UNLESS COND` -\> `!skipunless cond=COND`
-   `Include = FILE` -\> `!include file=FILE`
-   `dialects = DIALECTS` -\> `!dialects DIALECTS`
-   `exceptions = FILE` -\> `!exceptfile file=FILE`
-   `except = ID WORDS` -\>
    `!exception rule=ID   dialects=DIALECTS word=WORD`, once for each
    `WORD` in `WORDS`
-   `assert = DIAL WORD RESULT` -\>
    `!assert dialect=DIAL   word=WORD result=RESULT`
-   `conditions` -\> now on the command-line with `-D`

The following are no longer supported:

-   ``` `` ```; use a single `` ` `` in each part instead.
-   The `<<cat>>` category specification now needs single angle
    brackets.

The `%` on the end of a percentage is no longer required, and will
probably cause an error. Similarly, references to individual items
within `BEFORE` no longer need a hash character.

Finally, [mappings](#rcm) are sufficently different to require
individual attention. A mapping like `{1AB}` can probably be converted
to `<1B>`, and those like `{>}` can hopefullybe left alone, but it's
difficult to generalise otherwise.

Sample rules
------------

For fun, here are some rules which implement well-known sound changes.

### Palatalisation of velars

For example, in Slavic or Romance.

    velar   = kgxÉ£
    palatal = Ê§Ê¤ÊÊ
    front   = iÃ­Ã®eÃ©Ãª
    * <velar>j <1palatal> _        ! rakja -> raÊ§a
    * <velar>  <palatal>  _<front> ! raki -> raÊ§i

    * Kj C _  ! very concise alternative

### Hungarian-style vowel harmony

First of all:

    front = eÃ¸y
    back  = aou

If the harmony is dictated by the first vowel in the word:

    * <front> <back>  <back>.*_  B
    * <back>  <front> <front>.*_ B

If it's dictated by the last vowel in the word, we need a reverse banana
(and you were wondering what the point of that was, weren't you?):

    * <front> <back>  _.*<back>  R
    * <back>  <front> _.*<front> R

### i-umlaut

Using the categories previously defined:

    <back>   <front>   _<cons>+<+jiÃ­Ã®>

### Sievers' Law

This causes front vowels to appear before glides which follow heavy
syllables:

    C  = (consonants)
    G  = wj
    hi = ui
    V  = (all vowels)
    á¾»  = (long vowels)

    * CG 1{2hi}2   #|C|á¾»|VV|h_V B 

See if you can work out why you can't use zero in `BEFORE` here.
