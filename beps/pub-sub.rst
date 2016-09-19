:BEP: XXX
:Title: Publish/Subscribe Protocol
:Version: $Revision$
:Last-Modified: $Date$
:Author:  Steven Siloti <ssiloti@gmail.com>
:Status:  Draft
:Type:    Standards Track
:Content-Type: text/x-rst
:Created: 27-Aug-2016
:Post-History: 


Abstract
========

This BEP defines a modification of the DHT protocol [#BEP-5]_ to provide a topic based publish/subscribe service rather than a key/value store. Each topic is associated with a mutable item [#BEP-44]_. Messages are published as new values for the mutable item. A separate overlay network is maintained for each topic.


Rationale
=========

BEP 46 [#BEP-46]_ defines a standard format for publishing a torrent which can later be updated by its publisher using a mutable item. A downside of this method is that it relies on polling the DHT to receive updates. The DHT must be polled at a relatively low rate to avoid putting excessive load on the network. This limitation means there may be a significant delay between an update being published and a client receiving it. This BEP aims to provide a means of propagating updates with minimal delay by using push messages rather than polling.


Protocol
========

The pub/sub protocol is based on the DHT protocol [#BEP-5]_ with the following modifications:

The value of K is set to one.

The routing table's home bucket and its sibling SHOULD have a capacity of at least 8 nodes each. When the home bucket is split all but one node from the former home bucket's sibling SHOULD be evicted from the routing table.

Every query MUST contain a key ``c`` with a 20-byte string value. The value is used to identify which topic the message is intended for. The value MUST be set to the target hash of the mutable item associated with the topic.

The ``get_peers`` and ``announce_peer`` queries are prohibited.

Mutable ``get`` and ``put`` queries [#BEP-44]_ are only permitted for the mutable item associated with the topic.

The response to ``get`` queries SHOULD NOT contain a ``nodes`` or ``nodes6`` [#BEP-32]_ key.

If a ``put`` query contains a valid update it SHOULD be forwarded to all nodes in the routing table for the topic. An update is valid if the query is valid per BEP 44 [#BEP-44]_ and the value has a sequence number greater than the client's currently stored value. The query SHOULD be forwarded by generating new queries as if the client originated the request.


Subscribing to topics
=====================

Clients subscribe to a topic by joining that topic's overlay network. Clients bootstrap into a network by sending a ``get_peers`` query to the DHT with the ``info_hash`` field set to the target hash of the mutable item associated with the topic. Clients SHOULD also announce themselves to this infohash with the port they are listening for DHT messages on. Clients MUST treat each topic as a separate node with its own routing table and transaction state. Nodes for different topics with the same listen address SHOULD use the same node id. Clients SHOULD store the latest value of the mutable item associated with the topic at all times.


Publishing messages
===================

A client which intends to publish messages to a topic SHOULD also subscribe to the topic. When a new message is generated it SHOULD be sent to all peers in the client's routing table for the topic. Clients SHOULD NOT attempt to send a new value to all nodes subscribed to the topic.


References
==========

.. [#BEP-5] BEP_0005. DHT Protocol.
   (http://www.bittorrent.org/beps/bep_0005.html)
   
.. [#BEP-32] BEP_0032. BitTorrent DHT Extensions for IPv6.
   (http://www.bittorrent.org/beps/bep_0032.html)

.. [#BEP-44] BEP_0044. Storing arbitrary data in the DHT.
   (http://www.bittorrent.org/beps/bep_0044.html)
   
.. [#BEP-46] BEP_0046. Updating Torrents Via DHT Mutable Items.
   (http://www.bittorrent.org/beps/bep_0046.html)

   
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

