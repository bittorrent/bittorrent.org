#!/usr/bin/env python

import os
import sys

date = None
revision = None

if len(sys.argv) != 2:
    sys.stderr.write( "Usage: postprocess.py input > output\n" )
    sys.exit(-1)

for x in os.popen( "svn info %s" % sys.argv[1] ):
    tup = x.split(':')
    if len(tup) < 2:
        continue

    key = tup[0].strip()
    val = ":".join(tup[1:]).strip()
    if key == "Last Changed Rev":
        revision = val
    elif key == "Last Changed Date":
        date = val

fp = open(sys.argv[1], 'r')
for x in fp:
    # only process up to the first blank line, which signals the end of the BEP headers.
    if x == '':
        break

    if "$Revision$" in x:
        x = x.replace( "$Revision$", revision )

    if "$Date$" in x:
        x = x.replace( "$Date$", date )

    sys.stdout.write(x);

sys.stdout.write('\n');
for x in fp:
    sys.stdout.write(x);

