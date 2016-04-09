Geoff's Sound Change Applier
============================

Last update: 16 March 2009 (version 0.5)

About SCA
---------

Geoff's Sound Change Applier, **SCA** hereafter, is a program which
applies rule-based transformations to strings of Unicode text. It uses
[Python](http://www.python.org), which you'll need to install to be able
to use it; most Linices should have it already installed.

SCA was originally written as an aid for linguists and conlangers to
simulate the effects of the Neo-grammarian concept of sound-change and
is accordingly oriented towards this use, although it should be usable
for any similar non-linguistic task. It was originally based on [a C
program written by Mark Rosenfelder](http://www.zompist.com/sounds.htm),
which is fine for what it does, but I needed something more powerful for
my porpoises, which frequently require one word to be converted into
several descendants simultaneously. I recommend reading the
documentation for his program anyway, since although it works somewhat
differently from mine, many of the underlying concepts and principles
are the same.

SCA works well enough for me, and while I hope it will be found useful,
I can't guarantee that it will be suitable for your requirements; if
you've any comments or suggestions for improvements, let me know. It
works with Python 2.4 and 2.51, but not 1.5, for example.

New features in version 0.5 are marked accordingly. Features which are
described as "deprecated" will not be supported for much longer, and you
are advised to convert any existing files which use them.

Downloading
-----------

All of the necessary files are stored in this repository:

-   **scdefs.py scconv.py scrule.py sc.py sc\_apply.py**: The python
    implementation.
-   **README.md**: a copy of this file.
-   **spanish.sc**: sample file with very approximate sound changes from
    Latin to Spanish. It is most definitely *not* guaranteed to be
    authoritative!
-   **ipa.sc**: some definitions for use with IPA symbols.
-   **sc-mode.el**: syntax highlighting mode for GNU Emacs.

Using SCA
---------

SCA is invoked from the command-line like this:

    python sc_apply.py -c<sc-file> [arguments] <words>

**sc-file** is the name of the "rule file", which contains the change
rules; you must specify this, or the program won't work. You can use
`--scfile=` instead of `-c` if you prefer. The filename should end with
".sc"; this extension can be omitted from the command-line. The format
of the file is described below.

**words** are the words to process, separated by spaces. If no words are
supplied, and no `-l` argument is present, you will see the banner, but
nothing else interesting will happen.

All of the remaining arguments are optional.

-   `-q` or `--quiet`: don't print the starting banner.
-   `-lFILE` or `--input=FILE`: process words in the file called `FILE`.
    The words are assumed to be separated by spaces.
-   `-dDIALECTS` or `--dialects=DIALECTS`: output results for `DIALECTS`
    only. By default it is assumed that you want to see the results for
    all dialects.
-   `-eENCODING` or `--enc=ENCODING`: use `ENCODING` to represent
    strings. The default is "utf-8", so the program should handle
    Unicode with some degree of success.

If you have specified an input file, you can also use the following,
which are useful if you, for example, your input file has words and
meanings on the same line:

-   `-fFIELDS` or `--fields=FIELDS`: process only the words specified by
    `FIELDS`, which is a comma-separated list of one or more numbers or
    ranges. For example, `-f0` means "first field only", `1-3` means
    "second, third, and fourth fields", and `0,2-4` means "the first
    five fields excluding the second." Note that the first field is
    numbered zero.
-   `-FINSEP` or `--insep=INSEP`: use `INSEP` as the field delimiter.
    The default is whitespace. This character should not be a valid
    character in your orthography, otherwise the program won't know if
    it's read a field delimiter or not.

The following arguments affect the display of the output:

-   `-sSEP` or `--sep=SEP`: Output the results for all dialects on the
    same line, with SEP as a separator. This is useful if you want to
    view the output in a database or a program like OpenOffice Calc. It
    overrides all of the other options below.
-   `-m` or `--minimal`: Minimalistic output. This overrides all of the
    options below.
-   `-r` or `--rules`: Output each rule as it is processed in the
    original form.
-   `-R` or `--regexp`: Output each rule as it is processed as a regular
    expression. This is useful if you want to see what the program is
    actually working with.
-   `-a` or `--all`: By default, the previous two options only generate
    output when the word changes. Ths option will generate output each
    time.
-   `-C` or `--colour`: Add colour highlighting to the output. You will
    need an ANSI-capable terminal for this.
-   `-hN` or `--hlevel=N`: Only show headings up to level N. (0.5; this
    was previously called "-L").

The options `-R -a`, `-r -a`, and `-r` replace the options `-v1 -v2 -v3`
in earlier versions of the program. They are ignored if you read your
words from an input file, based on the entirely reasonable assumption
that they may generate far more output than you really want to look at.

As a simple example:

    python sc_apply.py -cspanish.sc flamma gutta ossu petra cu:pa
    >>> flamma
    S: llama
    >>> gutta
    S: gota
    >>> ossu
    S: hueso
    >>> petra
    S: piedra
    >>> cu:pa
    S: cuba

Of course, it can't get everything right; if you have any improvements,
let me know!

If you want to save your output to a file, on Linux and Window\$ just
add " `> name-of-file`" to the command-line. I don't know what to do on
a Mac.

Format of the rule file
-----------------------

Each line in the rule file is assumed to comprise of a **comment**, a
**definition**, a **rule**, a **directive**, or a blank line. Blank
lines - empty lines and lines consisting of nothing but whitespace -
play no part in the operation of the program and are ignored hereafter.
The program tries to be intelligent about an incorrectly formatted line,
but may not catch all errors.

**Comments** may be specified in two ways. Anything on a line after an
exclamation mark '!' (AKA bang, pling, cokebottle, and so on) is ignored
altogether. Alternatively, a line starting with a hash character '\#'
(AKA "pound sign", number sign, octothorpe, mesh, etc.) is also a
comment; if the hash is followed immediately by one or more colons
without intervening whitespace, the following text will be output if the
number of colons following the hash is less than or equal to the number
after the `-h` option.

    ! This is a comment which will be ignored
    foo = bar ! So is this
    # And this
    #: This will be printed with "-h1".
    #:: This won't, but "-h2" will show it.
    foo = bar # This is not a comment, and will generate an error message.

(0.5: much of this is new.)

**Directives** consist of the words `SKIP NOSKIP END`, which must appear
alone on a line. They may be used to disable rules if they're giving
problems:

-   `END` means that no further lines in the file will be processed.
-   All lines after `SKIP` will be ignored until `NOSKIP` is reached.
-   `SKIP if COND` and `SKIP unless COND` work like `SKIP` if or unless
    `COND` is given in a preceding `conditions =` definition. (New in
    0.5.)

Directives are provided for convenience and are not intended to
constitute full C-like preprocessing facilities. In particular, they do
not nest; `END` is obeyed even after `SKIP`.

**Definitions** have the format `name = value`, where any amount of
whitespace is permitted around the equals sign and in **value**, but not
in **name**. Three `name`s have special meaning:

-   `Include = FILE` will immediately read in the contents of the file
    named `FILE`, which is handy if, for example, you have a set of
    common definitions you want to use in several other files and don't
    want to cut-and-paste them in each time.
-   `dialects = DIAL` indicates that each character in `DIAL` is a
    separate dialect; the program will output one word for each dialect,
    and rules may be specified to operate on certain dialects only. For
    example, `dialects =        PGSCFOIR` might be used by someone who's
    interested in comparing cognates in the Romance languages. The
    characters must be uppercase or lowercase letters.
-   `conditions = COND1 COND2 COND3` is only meaningful in conjunction
    with directives. (New in 0.5.)

Otherwise, a definition defines a **category**, which is a group of
**symbols**. Symbols have no special meaning to the program and mean
whatever you want them to mean; in the context of sound-changes, for
example, they represent individual phonemes. A symbol may be any
non-space non-punctuation character, according to Python's definition;
this permits most Unicode characters.

A category `name` may be a single uppercase letter (this includes the
Greek and Russian alphabets, and accented characters), or two or more
letters in mixed case. Single-character names will convert your rules
from clear-but-verbose to concise-but-cryptic. The digits 1-9 are also
allowed providing that the name starts with a letter.

**value** is one or more sets of symbols separated by whitespace. If a
set is equal to the name of a previously defined category, the value of
that category is substituted. For example:

    cat1 = abc def  ! cat1 = "abcdef"
    cat2 = cat1 ghi ! cat2 = "abcdefghi"
    cat3 = ca t1    ! cat3 = "cat1"
    A    = abc Def  ! A    = "abcDef"
    B    = xyz      ! B    = "xyz"
    C    = A g h i  ! C    = "abcDefghi"
    D    = jkl      ! not allowed; "D" has previously been used as a symbol.
    E    = AB       ! E    = "AB"; don't do this either.
    F    = A B      ! F    = "abcxyz"; this is the correct way to do it.

The symbol "0" (zero) means "nothing", and may be used for padding.

(0.5: rules for `name` and `value` are more clearly defined.
Single-character names are permitted. Tildes are no longer necessary and
are deprecated.)

Rules
-----

This is the real meat of the program. There is a lot to take in here; be
patient.

A rule consists of four or five fields on a line, which are separated by
white space:

    DIALECTS   BEFORE  AFTER  ENV  FLAGS

`ENV` in turn consists of two fields, `PRE` and `POST`, separated by the
character '\_' (underscore); either or both of them may be empty.
Informally, this rule means "for each dialect in `DIALECTS`, `BEFORE`
changes to `AFTER` when preceded by `PRE` and followed by `POST`, using
`FLAGS` if any are specified."

`BEFORE` and `AFTER` must not be empty; if you really mean "nothing",
you must use '0' (i.e. zero).

`DIALECTS` is a string of letters or numbers which specify whch dialects
the rule applies to, or "\*" to mean "all dialects". You can pad the
dialect string with dots to make the file visually easier to follow
(0.5: dots only are permitted for this); for example:

    PGSC....  (rule applying to Portuguese, Galician, Spanish, and Catalan)
    ...CFO..  (ditto Catalan, French, and Occitian)

Alternatively, you can use . `DIALECTS` is omitted from the example
rules below.

`BEFORE`, `PRE`, and `POST` may consist of a sequence of one or more of
the following:

-   A symbol, which stands for itself.
-   A single-character category name, which represents the appropriate
    group of symbols.
-   A **category reference**, which is enclosed in
    `<angle        brackets>`, ditto.

For example, `Ta<cat>` means "a symbol from category `T` followed by the
symbol 'a' followed by a symbol from category `cat`".

`BEFORE`, `PRE`, and `POST` are all converted internally to reglar
expressions, and may thus contain the special regular expression
metacharacters. "." (a dot) may be used to represent "any character";
the most useful of the others are "|" (pipe, "either-or"), "?" (question
mark, for zero or one of the preceding), "\*" (asterix, zero or more),
and "+" (plus, one or more). Thus `h?C` means "`C`, optionally preceded
by `h`". Don't, however, use parentheses; you'll confuse the program.

Within `ENV`, `a_b` means "when preceded by 'a' and followed by 'b'";
`_` by itself, i.e. `PRE` and `POST` both empty, means "always". The
following characters have special meanings within `PRE` and `POST`:

| Character | Where valid     | Meaning                    |
| --------- | --------------- | -------------------------- |
| `#`       | `PRE`           | beginning of a word        |
| `#`       | `POST`          | end of a word              |
| `%`       | `PRE, POST`     | `BEFORE`                   |
| 0 (zero)  | `BEFORE, AFTER` | null phoneme, empty, blank |
| \<        | `AFTER, POST`   | `PRE`                      |
| \>        | `AFTER`         | `POST`                     |

"\`" (backquote) in `BEFORE` and `ENV` mean "use the corresponding field
on the previous rule". If `BEFORE` is "\`\`" (two backquotes), both it
and `ENV` are taken from the previous rule, and `ENV` is empty. You can
use the words `BEFORE`, `PRE`, and `POST` instead of "%", "\<", and "\>"
here and in mappings if you prefer. (0.5: all of these are new; \< is
allowed in `POST`.)

### Category references

Category references are enclosed in \<angle brackets\>. There are
several formats; the examples below assume that the following
definitions have been set up:

    cat = abcdef
    dog = ghijkl

| Format          | Meaning            | Equivalent                |
| --------------- | ------------------ | ------------------------- |
| \<cat\>         | Reference          | "abcdef", of course       |
| \<\^cat\>       | Complementation    | anything but "abcdef"     |
| \<cat+ghi\>     | Augmentation       | "abcdefghi"               |
| \<cat-ace\>     | Subtraction        | "bdf"                     |
| \<+ghi\>        | One-off reference  | "ghi"                     |
| \<-ghi\>        | One-off complement | anything other than "ghi" |
| \<\<cat,dog\>\> | Combination        | "abcdefghijkl"            |

'+' and '-' are new in 0.5, and are useful if you have a specific set of
symbols which you use once or twice and don't want to create a separate
category for them. The format `>abc<` is no longer supported in 0.5; use
`<+abc>` instead.

If `C` is defined as a category name, the angle brackets are not needed
if the symbols "\^", "+", and "-" are not present; i.e. `<C>` is
equivalent to `C`. The commas are not needed in the last format if all
the category names are single characters; `<<ABC>>` is thus the same as
`<<A,B,C>>`.

`AFTER` must consist of "0" (zero), a single category reference, or a
sequence of symbols, **indexes**, and **mappings**. If it contains just
a category reference, `BEFORE` must also contain just a category
reference, and the two categories must contain the same number of
symbols. The rule is then converted to the mapping `{%:BEFORE:AFTER}`.

(0.5: "\_" (underscore) is no longer permitted in `AFTER`, and is no
longer necessary anyway.)

An **index** consists of the '\#' character followed by an optional
minus sign and a digit `n`. `#n` means "the nth symbol in BEFORE,
counting from 1 at the start"; `#-n` means "the nth symbol in BEFORE,
counting from 1 at the end". Zero is not a valid digit in an index.

### Mappings

Mappings are new in 0.5, and replace the older format with backquotes,
which is deprecated.

A mapping is referred to as `{a:c1:c2}` (older `` a`c1`c2 ``), where
`c1` and `c2` are category names (\*not\* references), and means "the
symbol in `c2` which occupies the same position as `a` does in `c1`".
`c1` and `c2` must have the same number of symbols, and `a` is one of
the following:

-   A digit, with optional preceding minus sign. This specifies an
    index; the hash symbol is not necessary.
-   `<`, which means `PRE`.
-   `>`, which means `POST`.
-   `%`, which means `BEFORE`.

The colons may be omitted if `c1` and `c2` are both single-character
category names.

There are six shorthand mappings, in all of which `c2` is equivalent to
`BEFORE`:

| Mapping | a                 | c1     |
| ------- | ----------------- | ------ |
| `{>}`   | `POST`            | `POST` |
| `{<}`   | `PRE`             | `PRE`  |
| `{%>}`  | `BEFORE`          | `POST` |
| `{%<}`  | `BEFORE`          | `PRE`  |
| `{n>}`  | index in `BEFORE` | `POST` |
| `{n<}`  | index in `BEFORE` | `PRE`  |

Mappings are very powerful and should be properly understood before they
are used. For some examples, see the sample rules later on.

Flags
-----

The `FLAGS` field consists of zero or more characters, which alter the
way the rule works. At present, three flags are supported, and all
others are ignored.

The `P` flag will specify a rule as **persistent**: all persistent rules
are applied, in the order they appear in the file, after every other
rule. For example, a persistent nasal harmony rule like this:

    <nasal>    {>}     _<vstop>   P

will always ensure that nasals are homorganic to following voiced stops.

The `B` flag means "apply this rule until no further changes occur". It
is necessary to get around the ambiguity of the **banana problem**
(search for it in the [Jargon File](http://www.catb.org/~esr/jargon/))
when `PRE` and `POST` match the same characters ; for example, if you
have the following rule:

    n   z   <vowel>_<vowel>

"banana" will then be converted to "bazana", not "bazaza" as you
probably want. The point here is that Python's regular-expression
matcher thinks that "banana" contains one occurrence of "ana", whereas
we'd like it to think there are two. With the `B` flag, the rule will
work as we want:

    n   z   <vowel>_<vowel>   B

Beware! If some symbols appear in both `BEFORE` and `AFTER`, this won't
work. For example, if you try to do Welsh-style lenition like this:

    unlen = ptkbdg
    len   = bdgvDG
    vowel = aeiou

    <vstop>   <vfric>   <vowel>_<vowel>   B

then "apa" will become "ava". See if you can work out why.

The `R` flag is like the `B` flag, but operates from the end of the
word. For example, here's the rule for finding the weak and strong jers
in Slavonic:

    <strong> <weak>        _
    <weak>   <strong>      _<cons>+<weak> R

Example rules
-------------

And now, at last, here are some examples of how all of this works in
practice. Most of these use the categories defined in the file `ipa.sc`.

### Conversion

To convert one category to another in certain environments, simply do:

    <old>  <new>  foo_bar

where `foo` and `bar` can be anything you want; watch out for the banana
problem if they overlap. To ensure that the rule is applied only when
they are the same - for example, to delete something between two
identical vowels - replace `bar` with `<`:

    <old>  <new>  foo_<

### Loss

Use "0" (zero) for `AFTER`:

    <cons>+   0           _#

means "all consonants disappear at the end of a word". This would work
just as well without the "+" and with the `B` flag. But don't do this:

    <cat>X    <cat>       _

to mean "X disappears after something of category `cat1`". The correct
way is this:

    X         0           <cat1>_

### Conversion and loss

Suppose you have a symbol ":" which follows a vowel which is to be
lengthened. You can carry out the lengthening like this:

    <short>  <long>   _:
    :        0        <long>_

Better, however, is to use a mapping:

    <short>: <1:short:long>   _

### Metathesis

To make two or more symbols change places, use indexes in `AFTER`. For
example:

    <vowel><liquid>   #2#1   <stop>_<stop>

will change "tort" to "trot".

### Epenthesis

Use "0" (zero) for `BEFORE`:

    0    d     n_r

means "'nr' becomes 'ndr'". Of course, you could also do:

    nr    ndr     _

But you can generalise the rule to:

    0    {<:nasal:vstop}    <nasal>_<liquid>

which will also convert "ml" to "mbl", among others.

Here's a more dramatic example. This does Sievers' law in Indo-European,
which inserts a vowel between a heavy syllable and a glide; for example,
"andya" becomes "andiya":

    <cons><glide>   #1{2:glide:high}#2  #|<cons>|<long>|<vowel><vowel>_<vowel>

See if you can work out why you can't use zero in `BEFORE` here.

### Assimilation

Here is where mappings come into their own:

    <nasal>    {>}     _<vstop>

will convert, for example, "md" to "nd". For complete regressive
assimilation, to convert "md" and "nd" to "dd", use `>` in `AFTER`:

    <nasal>    >       _<vstop>

Note the difference between the mapping and the straightforward
substitution. For progressive assimilation, use `<` and `{<}` in
`AFTER`.

### Simplification

To reduce two consecutive occurrences of a symbol in category `cat` to
one, you can do this:

    <cat>    0     _%

or this:

    <cat>    0     %_

### Gemination

To turn one symbol into two, one of the following will work:

    0          <       x_whatever

if 'x' geminates before a particular environment;

    0          >       whatever_x

if it geminates after a particular environment;

    x          #1#1    whatever_whatever

if it's more complicated than that.

### Miscellany

Here are a few more rules from some of my files, with a minimum of
explanation.

#### Palatalisation of velars

    <velar>j   {1:velar:pal}  _
    Kj         {1KC}          _  ! very concise alternative

#### i-umlaut

    <backround>   <frontround>   _<cons>+j

#### Vowel harmony, Hungarian style

If the harmony is dictated by the first vowel in the word:

    <+eøy>  <+aou>   <+aou>.*_ B
    <+aou>  <+eøy>   <+eøy>.*_ B

If it's dictated by the last vowel in the word:

    <+eøy>  <+aou>   _.*<+aou> R
    <+aou>  <+eøy>   _.*<+eøy> R

Of course, you could use categories here.

### Environmental damage

You can use otherwise unused characters to temporarily represent
**environments**. For example, consider the following nasalisation rules
from one of my conlangs:

    0         ;          <vowel>_<nasal><obs>
    0         ;          <vowel>_<nasal><liquid>
    0         ;          <vowel>_<nasal>#
    a|u       ä          _;
    e|i       ë          _;
    á|â|ú|û   ü          _;
    é|ê|í|î   ï          _;
    ;    0          _

The first three rules set up the nasalisation environment, the next four
nasalise the vowels, and the last rule removes the environment since
it's no longer useful. Without this there would need to be twelve rules;
ordinarily, you might think you could do this:

    <vowel>   <nasvow>        _<nasal>(<obs>|<liquid>|#)

but the parentheses in `POST` would mess up the workings of the program.
Of course, in this case you can replace the last five rules with this:

    <vowel>;   {1:vowel:nasvow}        _

or the whole lot with:

    <vowel><nasal>   {1:vowel:nasvow}        _<obs>|<liquid>#

### Spelling

If the orthography and phonology of your language are related in
predictable ways, you can use SCA to convert between them. Note that
this sort of conversion is typically more complicated and fiddly than
merely converting sounds, especially if you have a complicated
orthography; this is probably where the use of one-off categories is
most useful. The last section of **spanish.sc**, which begins with the
comment "Spellings!", is a straightforward example. Here's another, from
a pre-Unicoded file for Liotan; this can be converted to two lines if
you use the appropriate mappings.

    c       ty      _
    q       dy      _
    L       ly      _
    ñ       ny      _
    R       ry      _
    x       kh      _
    S       sh      _
    Z       zh      _

Future enhancements
-------------------

These are just ideas at present and may or may not appear in future
versions, depending on my mood and the demand. Feedback will be
gratefully accepted.

### Environments

    @intervocalic  =  <vowel>_<vowel>

    <stop> <fric> @intervocalic

### Relations

This is an attempt to build featural relations into the system.

    &lenition = stop nasal -> fric nfric

    &lenition   @intervocalic

But is this really any better than:

    <<stop,nasal>>   <<fric,nfric>>  @intervocalic

?

### Modifiers

If you're dealing with long, short, nasal, and tonal vowels, it's
convenient to define categories to represent these as in **ipa.sc**,
where a particular diacritic represents a particular flavour of vowel.
The problem is that most diacritics are only available on lower and
uppercase `aeiouy`: there's no circumflexed `ø` in Unicode, for example,
and the non-ASCII IPA characters like epsilon and turned-C have no
accented variants at all. This means that if you have more than 12
separate vowel phonemes and want to use diacritcs, you're stuck, unless
you want to start using Greek or Cyrillic.

Ideally, we'd like to use the IPA diacritics instead, so that where we
currently have, for example, "á" for long /a:/, we'd need to use "a:"
where ":" represents the IPA length mark at 0x02D0. However, something
like this:

    <short>   <long>   foo_bar

should still work.

This all suggests that SCA should recognise certain symbols as
modifications of others. For example:

    MOD long = short :

would specify ":" to be a modifier of `short`, and the combination of a
`short` plus ":" would be recognised as a `\long`. Something like the
following could be used to spell modified categories properly, where '@'
removes the modifier:

    long   {@:short:long}   _

How this would work with vowels with more than one diacritic is,
however, not clear. If "\~" represents nasalisation, for example, should
"a:\~" or "a\~:" represent a long nasal vowel? How would these match
`long` and `nvowel`?
