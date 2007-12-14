tracker peer obfuscation extension
==================================

This extension extends the tracker protocol to support simple obfuscation
of the peers it returns, using the info hash as a shared secret between
the peer and the tracker. The obfuscation does not provide any security
against eavesdroppers that know the info-hash of the torrent, it does
however make it a lot harder for an eavesdropper to listen on tracker
traffic in general to pick up the responses.

The goal is to prevent internet service providers and other network
administrators to block or disrupt bittorrent traffic in general. It
will leave the possibility to block or disrupt bittorrent traffic for
a certain torrent (given the attacker knows the info-hash).

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
by another extension) MUST be bit-wise XORed by the info-hash.

In the case ``peers`` (or another filed containing peer info) is not a single
string, only the strings which contain the addresses and ports MUST be XORed.

The tracker response MUST remain a valid bencoded message.

backwards compatibility
-----------------------

A client that is configured to use this extension should always send the
``xor_ih`` to any new tracker first. If it fails, the standard ``info_hash``
parameter should be used instead. It is important to never send both
parameters in the same request, since that would defeat the purpose with
the shared secret (since the secret would be sent in plain text in the announce).

rationale
---------

The reason to XOR the info-hash with itself is because the tracker then
only need one extra lookup table for XORed hashes. Instead of applying
a scheme where a shared secret is exchanged. This will add no computational
overhead on the tracker for the torrent lookup.

authors
-------

| `Greg Hazel`__
| `David Harrison`__
| `Arvid Norberg`__

.. __: mailto:greg@bittorrent.com
.. __: mailto:dave@bittorrent.com
.. __: mailto:arvid@bittorrent.com

