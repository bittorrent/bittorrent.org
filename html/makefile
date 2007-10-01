all: ipv6_tracker_extension.html

%.html:%.rst
	~/docutils/tools/rst2html.py --link-stylesheet --stylesheet=css/screen.css --no-doc-title --no-toc-backlinks $? >$@


