
BEPS= \
	bep_0000.html \
	bep_0002.html \
	bep_0006.html \
	bep_0007.html \
	bep_0008.html \
	bep_0009.html \

all:	$(BEPS) 

%.html:%.rst
	~/docutils/tools/rstpep2html.py --template=../template.txt --cloak-email-addresses --link-stylesheet --stylesheet=../css/screen.css --no-toc-backlinks $? >$@ --traceback

	#~/docutils/tools/rst2html.py --template=../template.txt --cloak-email-addresses --link-stylesheet --stylesheet=../css/screen.css --no-doc-title --no-toc-backlinks $? >$@


