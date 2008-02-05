
BEPS= \
	bep_0000.html \
	bep_0001.html \
	bep_0002.html \
	bep_0003.html \
	bep_0004.html \
	bep_0005.html \
	bep_0006.html \
	bep_0007.html \
	bep_0008.html \
	bep_0009.html \
	bep_1000.html \

all:	$(BEPS) 

%.html:%.rst
	rstbep2html.py --template=template.txt --cloak-email-addresses --link-stylesheet --stylesheet=../css/bep.css --no-toc-backlinks $? >$@ --traceback

	#~/docutils/tools/rst2html.py --template=../template.txt --cloak-email-addresses --link-stylesheet --stylesheet=../css/screen.css --no-doc-title --no-toc-backlinks $? >$@


