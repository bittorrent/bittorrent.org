
# Be sure to commit changes to .rst files before building the html and then recommit with the updated html.
# Otherwise, the generated .html will have the svn revision number of the previous change rather than the
# current changes.

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
	bep_0010.html \
	bep_0012.html \
	bep_0015.html \
	bep_0016.html \
	bep_0017.html \
	bep_0018.html \
	bep_0019.html \
	bep_1000.html \

all:	$(BEPS) 

%.html:%.rst_post
	rstbep2html.py --template=template.txt --pep-base-url=http://www.bittorrent.org/beps/ --cloak-email-addresses --link-stylesheet --stylesheet=../css/bep.css --no-toc-backlinks $? >$@ --traceback

%.rst_post: %.rst
	python postprocess.py $? > $@ 

#%.html:%.rst
#	rstpep2html.py --template=template.txt --cloak-email-addresses --link-stylesheet --stylesheet=../css/bep.css --no-toc-backlinks $? >$@ --traceback



