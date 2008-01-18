
BEPS= \
	bep_0000_index.html \
	bep_0002_protocol.html \
	bep_0006_ipv6_tracker_extension.html \
	bep_0007_tracker_peer_obfuscation.html \
	bep_0008_metadata_extension.html \
	bep_0009_extension_protocol.html

all:	$(BEPS) 

%.html:%.rst
	~/docutils/tools/rstpep2html.py --template=../template.txt --cloak-email-addresses --link-stylesheet --stylesheet=../css/screen.css --no-toc-backlinks $? >$@ --traceback

	#~/docutils/tools/rst2html.py --template=../template.txt --cloak-email-addresses --link-stylesheet --stylesheet=../css/screen.css --no-doc-title --no-toc-backlinks $? >$@


