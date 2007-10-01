IPv6 tracker extension
======================

This extension extends the tracker response to better support IPv6 peers as
well as defines a way for multi homed machines to announce multiple addresses
at the same time. The main use case that this proposal is optimized for is
peers that are either on an IPv4 network running Teredo_ or peers that are on
an IPv6 network having an IPv4 tunnel interface.

.. _Teredo: https://www.microsoft.com/technet/network/ipv6/teredo.mspx

announce parameter
------------------

The client may add an ``&ipv6=`` parameter to the HTTP GET request it sends
to the tracker. The value is either an IPv6 endpoint (address and port) or
just an IPv6 address. In the case where only an address is supplied, the IPv6
port is assumed to be the same as specified by the ``&port=`` parameter.

The tracker should perform a NAT check on the IPv6 endpoint.

In case the client contacts the tracker on an IPv6 interface, the it may add
an ``&ipv4=`` parameter with its IPv4 address or endpoint. The value should
be either an IPv4 endpoint (address and port) or just an IPv4 address. If only
an address is supplied, the port is assumed to be the same as the ``&port=``
parameter.

The endpoints are encoded as strings as defined by `RFC 2732`_.

.. _`RFC 2732`: http://tools.ietf.org/html/rfc2732

If both an ``&ipv4=`` and an ``&ipv6=`` parameter are specified, the tracker
may ignore the address family that is the same as the source address of the
request. i.e. If the client connects to the tracker with an IPv4 source
address, the tracker may ignore any ``&ipv4=`` address and if the client
connects to the tracker with an IPv6 source address, the tracker may ignore
any ``&ipv6=`` parameter.

announce response
-----------------

In case the tracker does not support the ``compact`` response, no change is
necessary. Since the original ``peers`` response returns peer endpoints in
their expanded string form, IPv6 addresses can be passed back this way.

In case a compact response is requested, the tracker may add another key
to the response; ``peers6``. This key has the same layout as ``peers`` in
compact mode, but instead of using 6 bytes per endpoint, 18 bytes are used.
It only contains IPv6 addresses.

examples
--------

Example announce string with ``2001::53aa:64c:0:7f83:bc43:dec9`` as IPv6
address::

	GET /announce?peer_id=aaaaaaaaaaaaaaaaaaaa&info_hash=aaaaaaaaaaaaaaaaaaaa
	&port=6881&left=0&downloaded=100&uploaded=0&compact=1
	&ipv6=2001%3A%3A53Aa%3A64c%3A0%3A7f83%3Abc43%3Adec9

Example announce string with ``[2001::53aa:64c:0:7f83:bc43:dec9]:6882`` as IPv6 endpoint::

	GET /announce?peer_id=aaaaaaaaaaaaaaaaaaaa&info_hash=aaaaaaaaaaaaaaaaaaaa
	&port=6881&left=0&downloaded=100&uploaded=0&compact=1
	&ipv6=%5B2001%3A%3A53Aa%3A64c%3A0%3A7f83%3Abc43%3Adec9%5D%3A6882

Example announce string with ``2001::53aa:64c:0:7f83:bc43:dec9`` as IPv6
address and ``261.52.89.12`` as IPv4 address::

	GET /announce?peer_id=aaaaaaaaaaaaaaaaaaaa&info_hash=aaaaaaaaaaaaaaaaaaaa
	&port=6881&left=0&downloaded=100&uploaded=0&compact=1
	&ipv6=2001%3A%3A53Aa%3A64c%3A0%3A7f83%3Abc43%3Adec9&ipv4=261.52.89.12

Example response::

	d8:intervali1800e5:peers6:iiiipp6:peers618:iiiiiiiiiiiiiiiippe

rationale
---------

The naming of ``peers6`` is chosen not to collide with the current ``peers``
response and to be backwards compatible. It is also a simple addition to the
current response, using the same encoding.

authors
-------

| `Greg hazel`__
| `Arvid Norberg`__

.. __: mailto:greg@bittorrent.com
.. __: mailto:arvid@bittorrent.com

