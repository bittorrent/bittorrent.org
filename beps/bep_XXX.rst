:BEP: XXX
:Title: Magnet URI extension - Select specific file indices for download
:Version: $Revision$
:Last-Modified: $Date$
:Author: Tyler Houlihan <tchoulihan@gmail.com>
:Status:  Draft
:Type:    ??
:Content-Type: text/x-rst
:Created: 24-May-2017
:Post-History: 

Abstract
========

This magnet extension introduces the concept of an optional *select-only* file index array in the magnet URI, so that torrent clients can automatically select specific file(s) for download after the metadata has been downloaded.

Rationale
=========

For torrents with many files, it can be difficult to add the specific files you want to download. This extension would allow clients to know which specific files they should download. 

Also, many torrent clients have no way to *pause* the torrent after adding the magnet link and fetching the metadata. This means you must:

- Wait until the metadata downloads
- Pause the torrent
- And finally select the specific files you want. 

These problems could be eliminated by adding an *optional* array of file indices to the magnet link. 

This extension also creates the possibility of hosting library torrents, and creating magnet links which download subsets of the library. 

URI extension
===============
The new URI format would contain the following:

``magnet:?xt=urn:btih:HASH&dn=NAME&tr=TRACKER&so=0,2,4,6-8``

- ``so=0,2,4,6-8`` means *select only*, and the numbers are the file indices. Files are zero-indexed. Dashes mean inclusive ranges, so 6,7, and 8 are also added.

Special case: What if the magnet link is already added? 

Torrent clients that already have added that torrent should add any currently not-downloading file indices, and set their priority to normal. 


References
==========

Copyright
=========

This document has been placed in the public domain.



..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End: