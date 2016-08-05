:BEP: ??
:Title: Padding files and extended file attributes 
:Version: $Revision$
:Last-Modified: $Date$
:Author:  The 8472 <the8472.bep@infinite-source.de>
:Status:  Draft
:Type:    Standards Track
:Content-Type: text/x-rst
:Created: 05-Aug-2016
:Post-History: 


Padding files and extended file attributes
==========================================

This BEP specifies some additional file properties beyond those described those in BEP 3 [#BEP-3]_.


Multi-file format

.. parsed-literal::

    {
      "info":
      {
        "files":
        {[
          {
            "attr": "phxl",
            "sha1": *<20 bytes>*,
            "symlink path": ["dir1", "dir2", "target.ext"],
            ...
          },
          {
            ...
          }
        ]},
        ...
      },
      ...
    }
    
Single-file format

.. parsed-literal::


    {
      "info":
      {
        "attr": "hx",
        "sha1": *<20 bytes>*,
        ...
      },
      ...
    }




``attr``
  A variable-length string. When present the characters each represent a file attribute. l = symlink, x = executable, h = hidden, p = padding file. Characters appear in no particular order and unknown characters should be ignored.
  
``sha1``
  20 bytes. The SHA1 digest calculated over the contents of the file itself, without any additional padding. Can be used to aid file deduplication [#BEP-38]_.
  
``symlink path``
  An array of strings. Path of the symlink target relative to the torrent root directory.


Symlinks
========

When the ``l`` attribute flag is present then the ``symlink path`` represents the *target* of the symlink while ``path`` indicates the location of the symlink itself.
  
The ``length`` field of the symlink file should be zero. A non-zero length identical with the target file would improve backwards-compatibility but significantly complicate the management of piece hashing and duplicate pieces.
  
The target should be another file within the torrent, otherwise a dangling symlink will be created.
  
  
Padding files
=============

Padding files are synthetic files inserted into the file list to let the following file start at a piece boundary. That means their length should fill up the remainder of the piece length of the file that is supposed to be padded. For the calculation of piece hashes the content of padding file is all zeros.

Clients aware of this extension don't need to write the padding files to disk and should also avoid requesting their contents in ``BT_REQUEST`` messages, but for backwards-compatibility they must service such requests.

While clients implementing this extensions will have no use for the ``path`` of a padding file it should be included for backwards compatibility since it is a mandatory field in BEP 3 [#BEP-3]_.
The recommended path is ``[".pad", "N"]`` where N is the length of the padding file in base10. This way clients not aware of this extension will write the padding files into a single directory, potentially re-using padding files from other torrents also stored in that directory.

To eventually allow the path field to be omitted clients implementing this BEP should not require it to be present on padding files.  

Piece-aligned files simplify deduplication [#BEP-38]_ and the operations on mutable torrents [#BEP-39]_.

The presence of padding files does not imply that all files are piece-aligned.


Internally inconsistent torrents
================================

If used incorrectly or maliciously symlinks and padding files can result in internally inconsistent torrents which cannot finish downloading because they contain conflicting hash information. Similarly the ``sha1`` fields may in fact be inconsistent with the piece data and lead to failures after deduplication.

Clients should ensure that adding and deduplicating such a torrent does not lead to loss of already existing data. 




References
==========

.. [#BEP-3] BEP_0003. The BitTorrent Protocol Specification.
   (http://www.bittorrent.org/beps/bep_0003.html)

.. [#BEP-38] BEP_0038. Finding Local Data Via Torrent File Hints.
   (http://www.bittorrent.org/beps/bep_0038.html)

.. [#BEP-39] BEP_0039. Updating Torrents Via Feed URL.
   (http://www.bittorrent.org/beps/bep_0039.html)   
   