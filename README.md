<<<<<<< HEAD
# SSF_to_XML
LTRC IIIT HY - to create synthetic data
=======
# SSF format to XML format conversion


## Features

- **Extract Elements**: Parse input sentences to extract relevant elements such as words and their references.
- **Tag Coreferences**: Identify and tag coreferences in sentences, assigning unique identifiers to anaphoras and antecedents.
- **Color Mapping**: Generate random colors for visually distinguishing between different anaphoras and antecedents.
- **JSON Output**: Create a well-structured JSON output containing tagged text, metadata, and color mappings.

## Requirements

- import re
- import random
- import json
- import datetime
- from pytz import timezone

## Usage

- in 'input_file': give the SSF file needs to be converted 
- in 'output_directory': give the file directory to write the formated file/ press enter to download in downloads

## SSF sample data that can be converted to XML

<Sentence id="1">
1	((	BLK	<fs af='I,avy,,,,,,' head="I" name=NP1 poslcat="NM">
1.1	I	DEM	<fs af='I,avy,,,,,,' poslcat="NM" name="I">
	))		
2	((	NP	<fs af='rakaM,n,,pl,,o,ti,ti' head="rakAla" vpos="vib2" name=NP2>
2.1	reVMdu	QC	<fs af='reVMdu,n,,sg,,d,0,0'>
2.2	rakAla	NN	<fs af='rakaM,n,,pl,,o,ti,ti' name="rakAla">
	))		
3	((	NP	<fs af='manaswawvaM,n,,pl,,,0,0_V' head="manaswawvAlU" drel=k1:5 name=NP3>
3.1	manaswawvAlU	NN	<fs af='manaswawvaM,n,,pl,,,0,0_V' name="manaswawvAlU">
	))		
4	((	NP	<fs af='nenu,pn,any,sg,1,,ki,ki' vpos="vib1" head="nAku" drel=k4:5 name=NP4>
4.1	nAku	PRP	<fs af='nenu,pn,any,sg,1,,ki,ki' name="nAku">
	))		
5	((	VGF	<fs af='naccu,v,n,pl,3,,a,a' head="naccavu" name=NP5>
5.1	naccavu	VM	<fs af='naccu,v,n,pl,3,,a,a' name="naccavu">
5.2	.	SYM	<fs af='&dot;,punc,,,,,,'>
	))		
</Sentence>

<Sentence id="2">
1	((	NP	<fs af='bAlyaM,n,,sg,,d,0,0' head="nA" drel=k1:4 name=NP1>
1.1	nA	PRP	<fs af='nenu,pn,any,sg,1,o,ti,ti'><fs name=NP1 sentence id="1" REF=NP4 REFMOD=''> 
1.2	bAlyaM	NN	<fs af='bAlyaM,n,,sg,,d,0,0' name="bAlyaM">
	))		
2	((	NP	<fs af='nenu,pn,any,sg,1,,ki,ki' vpos="vib1" head="nAku" drel=k4:4 name=NP2>
2.1	nAku	PRP	<fs af='nenu,pn,any,sg,1,,ki,ki' name="nAku"><fs name=NP2 sentence id="1" REF=NP4 REFMOD=''>
	))		
3	((	NP	<fs af='bAgA,avy,,,,,0,0_avy' head="bAgA" name=NP3>
3.1	bAgA	INTF	<fs af='bAgA,avy,,,,,0,0_avy' name="bAgA">
	))		
4	((	VGF	<fs af='gurwuMdu,v,fn,sg,3,,A,A' head="gurwuMxi" name=NP4>
4.1	gurwuMxi	VM	<fs af='gurwuMdu,v,fn,sg,3,,A,A' name="gurwuMxi">
4.2	.	SYM	<fs af='&dot;,punc,,,,,,'>
	))		
</Sentence>

>>>>>>> d155a6e (Initial commit for SSF to XML convertion)
