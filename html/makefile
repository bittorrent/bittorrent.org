
all:	developer.html

%.html:%.rst
	~/docutils/tools/rst2html.py --template=template.txt --cloak-email-addresses --link-stylesheet --stylesheet=css/screen.css --no-doc-title --no-toc-backlinks $? >$@


