tracker peer obfuscation extension
==================================

This extends the tracker protocol to support simple obfuscation
of the peers it returns, using the info hash as a shared secret between
the peer and the tracker. The obfuscation does not provide any security
against eavesdroppers that know the info-hash of the torrent, it does
however make it a harder for an eavesdropper to listen on tracker
traffic in general to pick up the responses.

The goal is to prevent internet service providers and other network
administrators from blocking or disrupting bittorrent traffic 
connections that span between the receiver of a tracker response and any peer 
IP-port appearing in that tracker response.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are
to be interpreted as described in IETF `RFC 2119`_. 

.. _`RFC 2119`: http://tools.ietf.org/html/rfc2119


announce parameter
------------------

When using this extension, instead of passing the ``info_hash`` parameter
to the tracker, an ``xor_ih`` is passed.

The value of ``xor_ih`` MUST be the info-hash of the torrent, bit-wise XORed
with the byte-wise reverse of itself.

For example. If the info-hash is ``0102030405060708090a0b0c0d0e0f1011121314``
(hex encoded), the value passed as the ``xor_ih`` should be:
``0102030405060708091011121314`` XOR ``1413121110090807060504030201``. The
value MUST be url encoded, just like the ``info_hash``.

This extension does not change the semantics of any parameter.

announce response
-----------------

If the tracker supports this extension, the response should be exactly the
same as if the ``info_hash`` was passed, except that any field that contains
peer information (such as ``peers``, ``peers6`` or any other field defined
by another extension) MUST be bit-wise XORed by the info-hash.  So that
XORed peer lists can be precomputed and retained in tracker memory 
without sacrificing the tracker's ability to return a random subset of
peers, each ip-port pair MUST be XORed independently aligned to the 
beginning of the infohash.

In the case ``peers`` (or another filed containing peer info) is not a single
string, only the strings which contain the addresses and ports MUST be XORed.

The tracker response MUST remain a valid bencoded message.

backwards compatibility
-----------------------

Trackers that support obfuscation are identified in the .torrent file
by the inclusion of the letter 'o' following 'http' in the URL, e.g.,
httpo://tracker.bittorrent.com.  

A client that is configured to use this extension should always send the
``xor_ih`` to any tracker supporting 'o'.   Peers that do not recognize
the 'httpo' will not contact that tracker.   If the tracker wishes
to allow legacy peers to connect to the tracker then the announce
URL should appear twice in the announce list.  Once with the 'httpo' and 
once with 'http'.  Even if a tracker appears twice in the announce list,
if the tracker appears with an 'httpo' protocol in any announce URL, then
peers that support obfuscation SHOULD NOT query the tracker without 
obfuscation since this would enable an attack where ISPs always discard 
the first tracker request.

Peers SHOULD never send both infohash and XOR'd infohash
parameters in the same request, since that would defeat the purpose of 
the shared secret.

rationale
---------

By XORing the info-hash with itself the tracker is able to identify
torrents without sending the plaintext infohash and without
requiring an additional prior exchange of a shared secret.
Where trackers now maintain mappings from infohash to the 
corresponding torrent's peerlist and other torrent-specific state.  
Trackers would need one additional mapping from XORed infohash to 
the existing torrent's state.   If XORed peerlists are precomputed then
this method adds no computational overhead when a peer queries the
tracker for a peerlist.

This method requires decidedly less computational or communication
overhead than SSH or similar symmetric encryption methods.


authors
-------

| `Greg Hazel`__
| `David Harrison`__
| `Arvid Norberg`__

.. __: mailto:greg@bittorrent.com
.. __: mailto:dave@bittorrent.com
.. __: mailto:arvid@bittorrent.com

