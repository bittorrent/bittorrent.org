
BEPs are written as reStructured Text (.rst) files.
To create a .html from a .rst file, use python docutils.
This directory contains a makefile that runs rst2html.

1. Download docutils from http://docutils.sourceforge.net/
2. The makefile assumes docutils is located at ~/docutils
   If not then change the path in the makefile.
3. Add file(s) to be rendered into html to the "all:" in the makefile.
4. run make. 

