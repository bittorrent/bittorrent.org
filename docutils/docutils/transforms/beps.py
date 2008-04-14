# $Id: peps.py 4564 2006-05-21 20:44:42Z wiemann $
# Author: David Goodger <goodger@python.org>
# Author: David Harrison modified for BEPs (dave@bittorrent.com)
# Copyright: This module has been placed in the public domain.

"""
Transforms for BEP processing.

- `Headers`: Used to transform a BEP's initial RFC-2822 header.  It remains a
  field list, but some entries get processed.
- `Contents`: Auto-inserts a table of contents.
- `BEPZero`: Special processing for BEP 0.
"""

__docformat__ = 'reStructuredText'

import sys
import os
import re
import time
from docutils import nodes, utils, languages
from docutils import ApplicationError, DataError
from docutils.transforms import Transform, TransformError
from docutils.transforms import parts, references, misc


class Headers(Transform):

    """
    Process fields in a BEP's initial RFC-2822 header.
    """

    default_priority = 360

    # NOTE: There is no bep_base_url.  The base of the BEP directory is specified with pep_base_url
    # because changing this requires modifying the rst repository.   This value can be changed with the pep-base-url
    # argument.  For now, I don't want to modify restructured text parsing code.  It means we cannot currently
    # disambiguate between peps and beps for specifying the base url.
    bep_url = 'bep-%04d'
    bep_cvs_url = ('http://bittorrent.org/trac/browser/dotorg/trunk/html/beps/bep_%04d.rst' )
    #bep_cvs_url = ('http://svn.bittorrent.com/view/*checkout*'
    #               '/peps/trunk/bep-%04d.txt')
    rcs_keyword_substitutions = (
          (re.compile(r'\$' r'RCSfile: (.+),v \$$', re.IGNORECASE), r'\1'),
          (re.compile(r'\$[a-zA-Z]+: (.+) \$$'), r'\1'),)

    def apply(self):
        if not len(self.document):
            # @@@ replace these DataErrors with proper system messages
            raise DataError('Document tree is empty.')
        header = self.document[0]
        if not isinstance(header, nodes.field_list) or \
              'rfc2822' not in header['classes']:
            raise DataError('Document does not begin with an RFC-2822 '
                            'header; it is not a BEP.')
        bep = None
        for field in header:
            if field[0].astext().lower() == 'bep': # should be the first field
                value = field[1].astext()
                try:
                    bep = int(value)
                    cvs_url = self.bep_cvs_url % bep
                except ValueError:
                    bep = value
                    cvs_url = None
                    msg = self.document.reporter.warning(
                        '"BEP" header must contain an integer; "%s" is an '
                        'invalid value.' % bep, base_node=field)
                    msgid = self.document.set_id(msg)
                    prb = nodes.problematic(value, value or '(none)',
                                            refid=msgid)
                    prbid = self.document.set_id(prb)
                    msg.add_backref(prbid)
                    if len(field[1]):
                        field[1][0][:] = [prb]
                    else:
                        field[1] += nodes.paragraph('', '', prb)
                break
        if bep is None:
            raise DataError('Document does not contain an RFC-2822 "BEP" '
                            'header.')
        if bep == 0:
            # Special processing for BEP 0.
            pending = nodes.pending(BEPZero)
            self.document.insert(1, pending)
            self.document.note_pending(pending)
        if len(header) < 2 or header[1][0].astext().lower() != 'title':
            raise DataError('No title!')
        for field in header:
            name = field[0].astext().lower()
            body = field[1]
            if len(body) > 1:
                raise DataError('BEP header field body contains multiple '
                                'elements:\n%s' % field.pformat(level=1))
            elif len(body) == 1:
                if not isinstance(body[0], nodes.paragraph):
                    raise DataError('BEP header field body may only contain '
                                    'a single paragraph:\n%s'
                                    % field.pformat(level=1))
            elif name == 'last-modified':
                date = time.strftime(
                      '%d-%b-%Y',
                      time.localtime(os.stat(self.document['source'])[8]))
                if cvs_url:
                    body += nodes.paragraph(
                        '', '', nodes.reference('', date, refuri=cvs_url))
            else:
                # empty
                continue
            para = body[0]
            if name == 'author':
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.replace_self(mask_email(node))
            elif name == 'discussions-to':
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.replace_self(mask_email(node, bep))
            elif name in ('replaces', 'replaced-by', 'requires'):
                newbody = []
                space = nodes.Text(' ')
                for refbep in re.split(',?\s+', body.astext()):
                    bepno = int(refbep)
                    newbody.append(nodes.reference(
                        refbep, refbep,
                        refuri=(self.document.settings.pep_base_url
                                + self.bep_url % bepno)))
                    newbody.append(space)
                para[:] = newbody[:-1] # drop trailing space
            elif name == 'last-modified':
                utils.clean_rcs_keywords(para, self.rcs_keyword_substitutions)
                if cvs_url:
                    date = para.astext()
                    para[:] = [nodes.reference('', date, refuri=cvs_url)]
            elif name == 'content-type':
                bep_type = para.astext()
                uri = self.document.settings.pep_base_url + self.bep_url % 12
                para[:] = [nodes.reference('', bep_type, refuri=uri)]
            elif name == 'version' and len(body):
                utils.clean_rcs_keywords(para, self.rcs_keyword_substitutions)


class Contents(Transform):

    """
    Insert an empty table of contents topic and a transform placeholder into
    the document after the RFC 2822 header.
    """

    default_priority = 380

    def apply(self):
        language = languages.get_language(self.document.settings.language_code)
        name = language.labels['contents']
        title = nodes.title('', name)
        topic = nodes.topic('', title, classes=['contents'])
        name = nodes.fully_normalize_name(name)
        if not self.document.has_name(name):
            topic['names'].append(name)
        self.document.note_implicit_target(topic)
        pending = nodes.pending(parts.Contents)
        topic += pending
        self.document.insert(1, topic)
        self.document.note_pending(pending)


class TargetNotes(Transform):

    """
    Locate the "References" section, insert a placeholder for an external
    target footnote insertion transform at the end, and schedule the
    transform to run immediately.
    """

    default_priority = 520

    def apply(self):
        doc = self.document
        i = len(doc) - 1
        refsect = copyright = None
        while i >= 0 and isinstance(doc[i], nodes.section):
            title_words = doc[i][0].astext().lower().split()
            if 'references' in title_words:
                refsect = doc[i]
                break
            elif 'copyright' in title_words:
                copyright = i
            i -= 1
        if not refsect:
            refsect = nodes.section()
            refsect += nodes.title('', 'References')
            doc.set_id(refsect)
            if copyright:
                # Put the new "References" section before "Copyright":
                doc.insert(copyright, refsect)
            else:
                # Put the new "References" section at end of doc:
                doc.append(refsect)
        pending = nodes.pending(references.TargetNotes)
        refsect.append(pending)
        self.document.note_pending(pending, 0)
        pending = nodes.pending(misc.CallBack,
                                details={'callback': self.cleanup_callback})
        refsect.append(pending)
        self.document.note_pending(pending, 1)

    def cleanup_callback(self, pending):
        """
        Remove an empty "References" section.

        Called after the `references.TargetNotes` transform is complete.
        """
        if len(pending.parent) == 2:    # <title> and <pending>
            pending.parent.parent.remove(pending.parent)


class BEPZero(Transform):

    """
    Special processing for BEP 0.
    """

    default_priority =760

    def apply(self):
        visitor = BEPZeroSpecial(self.document)
        self.document.walk(visitor)
        self.startnode.parent.remove(self.startnode)


class BEPZeroSpecial(nodes.SparseNodeVisitor):

    """
    Perform the special processing needed by BEP 0:

    - Mask email addresses.

    - Link BEP numbers in the second column of 4-column tables to the BEPs
      themselves.
    """

    bep_url = Headers.bep_url

    def unknown_visit(self, node):
        pass

    def visit_reference(self, node):
        node.replace_self(mask_email(node))

    def visit_field_list(self, node):
        if 'rfc2822' in node['classes']:
            raise nodes.SkipNode

    def visit_tgroup(self, node):
        self.bep_table = node['cols'] == 4
        self.entry = 0

    def visit_colspec(self, node):
        self.entry += 1
        if self.bep_table and self.entry == 2:
            node['classes'].append('num')

    def visit_row(self, node):
        self.entry = 0

    def visit_entry(self, node):
        self.entry += 1
        if self.bep_table and self.entry == 2 and len(node) == 1:
            node['classes'].append('num')
            p = node[0]
            if isinstance(p, nodes.paragraph) and len(p) == 1:
                text = p.astext()
                try:
                    bep = int(text)
                    ref = (self.document.settings.pep_base_url
                           + self.bep_url % bep)
                    p[0] = nodes.reference(text, text, refuri=ref)
                except ValueError:
                    pass


non_masked_addresses = ('beps@bittorrent.org',
                        'bittorrent-list@bittorrent.org',
                        'bittorrent-dev@bittorrent.org')

def mask_email(ref, bepno=None):
    """
    Mask the email address in `ref` and return a replacement node.

    `ref` is returned unchanged if it contains no email address.

    For email addresses such as "user@host", mask the address as "user at
    host" (text) to thwart simple email address harvesters (except for those
    listed in `non_masked_addresses`).  If a BEP number (`bepno`) is given,
    return a reference including a default email subject.
    """
    if ref.hasattr('refuri') and ref['refuri'].startswith('mailto:'):
        if ref['refuri'][8:] in non_masked_addresses:
            replacement = ref[0]
        else:
            replacement_text = ref.astext().replace('@', '&#32;&#97;t&#32;')
            replacement = nodes.raw('', replacement_text, format='html')
        if bepno is None:
            return replacement
        else:
            ref['refuri'] += '?subject=BEP%%20%s' % bepno
            ref[:] = [replacement]
            return ref
    else:
        return ref
