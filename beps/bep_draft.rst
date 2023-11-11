:BEP: XXX
:Title: TLS extension
:Version: $Revision$
:Last-Modified: $Date$
:Author:  Darren Horrocks <mihael1peklar@gmail.com>
:Status:  Draft
:Type:    Standards Track
:Content-Type: text/x-rst
:Created: 11-Nov-2023
:Post-History: 11-Nov-2023: initial version


The TLS Extension introduces a single new command, TLS.

This is enabled by setting the third least significant bit of the
next to last reserved byte in the BitTorrent handshake:

::

  reserved[6] |= 0x04

The extension is enabled only if both ends of the connection set this bit.

Command
==================

::

  *TLS*: <len=0x0005> <op=0x20><port>

Sending the command is entirely optional. 
Disconnecting the current connection and reconnecting via TLS is also optional should the command be sent. 
No assumptions should be made about the clients ability to handle TLS based connections.

A TLS connection
==================

A serving peer should have a TLS server certificate where the CN is equal to the PeerID of the serving peer.

A client peer should validate that the PeerID matches the certificate CN.