#!/usr/bin/env python

# Author: David Goodger <goodger@python.org>
# Author: David Harrison <dave@bittorrent.com>
# Copyright: This module has been placed in the public domain.

# This is almost identical to rstpep2html.py --David Harrison


"""
A minimal front end to the Docutils Publisher, producing HTML from PEP
(Python Enhancement Proposal) documents.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description


description = ('Generates (X)HTML from reStructuredText-format BEP files.  '
               + default_description)

publish_cmdline(reader_name='bep', writer_name='bep_html',
                description=description)
