##############################################################################

# This is a sample .sc file to illustrate Geoff's Sound Change Applier.

# It converts a Latin word to an approximation of its Spanish cognate,
# using the sound changes in "A History of the Spanish Language" by
# R. Penny. The results are supposed to be illustrative rather than
# definitive, so rely on it for Latin to Spanish translations!

# Nouns should be in the accusative singular; long vowels should be
# indicated by a following colon.

# Someday, somebody should convert this to use Unicode and the IPA.

##############################################################################

# A list of letters identifying the daughter dialects which the file
# generates. In this case there's just Spanish.

dialects	=	S

# Define some classes of vowel phonemes.

vowel	=	ieEaOou
longv	=	íéÉáÓóú
front	=	ieE
back	=	uoO
lomid	=	EO
mid	=	eo
high	=	iu

# Define some classes of consonant phonemes.
# c C q are used for Old Spanish /ts tS dz/.

ustop	=	ptk
vstop	=	bdg
vfric	=	BDG
ufric	=	fTx
usib	=	csS
vsib	=	qzZ
nasal	=	mnN
liquid	=	lrR
glide	=	jw
alv	=	tcCsdqzlnr
lab	=	pbv
res	=	lrns

# when one of these consonants is final, stress is normally on final syllable

acons	=	bcdfghjklmpqrtvwxzBCDFGHJKLMPQRTWXZ

# These classes are combinations of others.

fric	=	vfric ufric
uobs	=	ustop usib
vobs	=	vstop vsib
obs	=	uobs vobs
cons	=	obs nasal liquid fric glide
cnotl	=	obs nasal fric

##############################################################################

# First of all, convert Latin spelling to the phonemic representation.

S	c|q	k	_
S	x	ks	_
S	y	i	_
S	ph	f	_

# Lose final /m/ and initial /h/.

S	m	0	_#
S	h	0	_

# Reduction of diphthongs and creation of prevocalic glides.

S	ae	E:	_
S	oe	e:	_
S	au	o:	_
S	<high>	<glide>	_<vowel>
S	e	j	_<vowel>

##############################################################################

# Assign the stress, indicated with a preceding ';', to the correct
# vowel. The antipenultimate is provisionally stressed; this stress is
# removed if the penultimate should be stressed.

# added to account for words of two short syllables.  ASh 2003 May 24
S	0	;	#<cons>*_<vowel>

S	0	;	_<vowel>:?<cons>*<vowel><cons>*<vowel><cons>*#
S	0	;	_<vowel>:<cons>*<vowel>+<cons>*#
S	0	;	_<vowel><cons><cons>+<vowel>+<cons>*#

#S	;	0	;.*_
S	;	0	_.*;
S	;	0	_.*;

# Convert from 'a:' to 'á'.

S	<vowel>	<longv>	_:
S	:	0	_

# Vulgar Latin vowel changes 1: short vowels get lowered.

S	i	é	_
S	u	ó	_
S	e	E	_
S	o	O	_
S	<longv>	<vowel>	_

# Vulgar Latin vowel changes 2: /E O/ merge with /e o/.
# The '@' is necessary to preserve the vowel when stressed;
# this is a bit of a crock.

S	;E	@	_
S	E	e	_
S	@	;E	_
S	;O	@	_
S	O	o	_
S	@	;O	_

##############################################################################

# Merger of /b/ and /v/.

S	v	B	_
S	b	B	<vowel>_;?<vowel>

# Palatisation of velars before fromt vowels.

S	sk	cc	_;?<front>|j
S	kk	cc	_;?<front>|j
S	k	c	_;?<front>|j
S	g	J	_;?<front>|j
S	j	0	c|J_

# Loss of intertonic vowels in various environments.
# -- Too much? (Anton)

S	<mid>|<high>	0	;<vowel><res>_<cons>+<vowel>
S	<mid>|<high>	0	;<vowel><cons>_<res><vowel>
S	<mid>|<high>	0	<vowel><res>_<cons>;<vowel>
S	<mid>|<high>	0	<vowel><cons>_<res>;<vowel>

# Syllable-final velars become /j/.

S	k	j	._t|l|s
S	g	j	._n|l

# Simplification of various clusters:
# pt ps rs ns mn mb > tt ss ss s nn mb

S	p	t	_t
S	p	s	_s
S	r	s	_s
S	n	0	_s
S	m	n	_n
S	n	m	_b

# More palatisations.

S	ptj	cc	_
S	ktj	cc	_
S	skj	cc	_
S	kkj	cc	_
S	tj	c	_
S	kj	c	_

##############################################################################

# Raising and diphthongisation of some vowels.

S	o	u	_n?j
S	<mid>	<high>	_<lab>j
S	<mid>	<high>	_<cons><cons>j
S	<lomid>	<mid>	_<cons>+j
S	;E	j;e	_
S	;O	w;e	_

# A few more palatisations.

S	jt	C	_
S	js	S	_
#S	f	h	_<glide>?;?<vowel>
S	f	h	#|<vowel>_<glide>?;?<vowel>
S	j	J	#_;?<vowel>

S	lj	L	_
S	n+j	N	_
S	dj	JJ	_
S	gj	JJ	_

S	pj	jp	._
S	rj	jr	._
S	L	Z	_

# Tense resonants.

S	ll	L	<vowel>_;?<vowel>
S	nn	N	<vowel>_;?<vowel>
S	rr	R	<vowel>_;?<vowel>

##############################################################################

# Lenition.

S	<vstop>	<vfric>	<vowel>|<liquid>_;?<vowel>|<liquid>|<glide>
S	<vstop>	<vfric>	<vowel>|<liquid>_;?<vowel>|<liquid>|<glide>
S	<uobs>	<vobs>	<vowel>|<liquid>_;?<vowel>|<liquid>|<glide>
S	<uobs>	<vobs>	<vowel>|<liquid>_;?<vowel>|<liquid>|<glide>
S	J	0	<vowel>|<liquid>_;?<vowel>|<liquid>|<glide>
S	<obs>	0	_%

# Initial Cl > L

S	pl	L	#_;?<vowel>
S	kl	L	#_;?<vowel>
S	fl	L	#_;?<vowel>

# Loss of remaining intertonic vowels.
# FIXME: too broad? (Anton)

S	<mid>|<high>	0	;<vowel><cons>_<cons>+<vowel>
#S	<mid>|<high>	0	<cons>_<cons>;<vowel>
S	<mid>|<high>	0	<vowel><cons>_<cons>;<vowel>

# Some glide changes.

S	sj	js	<vowel>_
#S	j	i	<vowel>_
#S	w	u	<vowel>_
S	aw	o	_
S	ow	o	_
S	aj	e	_
S	ej	e	_
S	ij	i	_

# Final vowels.

S	u	o	_#
S	i	e	_#
S	e	0	<vowel><alv>_#

# Some consonant cluster simplifications.

S	mt|nt	nd	_
S	nk	ng	_
S	L	l	_<cons>
S	N	n	_<cons>
S	R	r	_<cons>

S	dn	n	_
S	ct	q	_
S	Dc	q	_
S	ptm	m	_
S	mm	m	_

# note: ndc also > nc

S	ndc	ng	_
S	rdc	rc	_
S	ntc	nc	_
S	mpt	nt	_
S	skp	sp	_
S	spt	st	_
S	stk	sk	_

# note: these also > lm, ngl
S	nm	rm	_
S	ngn	ngr	_

S	ndn	ndr	_
S	mn	mbr	_

S	tn	nd	_
S	tl	ld	_
S	nr	ndr	_
S	ml	mbl	_

S	<lab>	w	<vowel>_<cons>
S	w	0	<back>_
S	l	w	a_q

S	t|d	q	._<cnotl>

S	b	u	_d
S	B	u	_<obs>
S	B	b	_

# FIXME: just _d?

##############################################################################

# Devoicing and separation of sibilants.

S	J	j	_
S	jj	j	_

S	<vsib>	<usib>	_

S	c	T	_
S	S|Z	x	_

# Spellings!
# Much altered by Anton Sherwood, 2003 May 20

S	T	z	_
S	z	c	_;?<front>|j

S	j	y	_
S	L	ll	_
S	R	rr	_
S	N	ñ	_
S	w	hw	#|<vowel>_;?<vowel>

S	<vfric>	<vstop>	_
S	k	qu	_;?<front>|y
S	k	c	_
S	C	ch	_

S	x	j	_
S	j	g	_;?<front>|y

S	<vowel>	<longv>	<vowel>.*;_n?s?#
S	<vowel>	<longv>	;_.*<vowel>.*<vowel>
S	<vowel>	<longv>	;_.*<vowel><acons>#
S	;	0	_
S	w	u	_
S	y	hi	#_e
S	y	i	<cons>_
S	y	i	_<cons>

S	0	e	#_s<cons>

##############################################################################
