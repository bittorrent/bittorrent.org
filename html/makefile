all: ipv6_tracker_extension.html \
	tracker_peer_obfuscation.html \
	extension_protocol.html \
	metadata_extension.html

%.html:%.rst
	~/docutils/tools/rst2html.py --template=template.txt --cloak-email-addresses --link-stylesheet --stylesheet=css/screen.css --no-doc-title --no-toc-backlinks $? >$@


