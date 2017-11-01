#!/usr/bin/env python3

"""
Reference generator for bittorrent v2 metadata.
Bencode implementation copied from https://github.com/utdemir/bencoder/
"""

import re
import string
import itertools as it
import os
from hashlib import sha1, sha256


BLOCK_SIZE = 2**14 # 16KB

def encode(obj):
    """
    bencodes given object. Given object should be a int,
    bytes, list or dict. If a str is given, it'll be
    encoded as UTF-8.

    >>> [encode(i) for i in (-2, 42, b"answer", b"")] \
            == [b'i-2e', b'i42e', b'6:answer', b'0:']
    True
    >>> encode([b'a', 42, [13, 14]]) == b'l1:ai42eli13ei14eee'
    True
    >>> encode({b'bar': b'spam', b'foo': 42, b'mess': [1, b'c']}) \
            == b'd3:bar4:spam3:fooi42e4:messli1e1:cee'
    True
    """

    if isinstance(obj, int):
        return b"i" + str(obj).encode() + b"e"
    elif isinstance(obj, bytes):
        return str(len(obj)).encode() + b":" + obj
    elif isinstance(obj, str):
        return encode(obj.encode("utf-8"))
    elif isinstance(obj, list):
        return b"l" + b"".join(map(encode, obj)) + b"e"
    elif isinstance(obj, dict):
        if all(isinstance(i, bytes) for i in obj.keys()):
            items = list(obj.items())
            items.sort()
            return b"d" + b"".join(map(encode, it.chain(*items))) + b"e"
        else:
            raise ValueError("dict keys should be bytes " + str(obj.keys()))
    raise ValueError("Allowed types: int, bytes, list, dict; not %s", type(obj))

def decode(s):
    """
    Decodes given bencoded bytes object.

    >>> decode(b'i-42e')
    -42
    >>> decode(b'4:utku') == b'utku'
    True
    >>> decode(b'li1eli2eli3eeee')
    [1, [2, [3]]]
    >>> decode(b'd3:bar4:spam3:fooi42ee') == {b'bar': b'spam', b'foo': 42}
    True
    """
    def decode_first(s):
        if s.startswith(b"i"):
            match = re.match(b"i(-?\\d+)e", s)
            return int(match.group(1)), s[match.span()[1]:]
        elif s.startswith(b"l") or s.startswith(b"d"):
            l = []
            rest = s[1:]
            while not rest.startswith(b"e"):
                elem, rest = decode_first(rest)
                l.append(elem)
            rest = rest[1:]
            if s.startswith(b"l"):
                return l, rest
            else:
                return {i: j for i, j in zip(l[::2], l[1::2])}, rest
        elif any(s.startswith(i.encode()) for i in string.digits):
            m = re.match(b"(\\d+):", s)
            length = int(m.group(1))
            rest_i = m.span()[1]
            start = rest_i
            end = rest_i + length
            return s[start:end], s[end:]
        else:
            raise ValueError("Malformed input.")

    if isinstance(s, str):
        s = s.encode("utf-8")

    ret, rest = decode_first(s)
    if rest:
        raise ValueError("Malformed input.")
    return ret

def root_hash(hashes):
    """
    Compute the root hash of a merkle tree with the given list of leaf hashes
    """
    # the number of hashes must be a power of two
    assert len(hashes) & (len(hashes) - 1) == 0
    while len(hashes) > 1:
        hashes = [sha256(l + r).digest() for l, r in zip(*[iter(hashes)]*2)]
    return hashes[0]

class FileHasher:
    def __init__(self, path, piece_length):
        self.path = path
        self.length = 0
        self.piecesv1 = []
        self.piecesv2 = []
        blocks_per_piece = piece_length // BLOCK_SIZE
        with open(path, 'rb') as f:
            while True:
                residue = piece_length
                blocks = []
                v1hasher = sha1()
                for i in range(blocks_per_piece):
                    block = f.read(BLOCK_SIZE)
                    if len(block) == 0:
                        break
                    self.length += len(block)
                    residue -= len(block)
                    blocks.append(sha256(block).digest())
                    v1hasher.update(block)
                if len(blocks) == 0:
                    break
                if len(blocks) != blocks_per_piece:
                    # If the file is smaller than one piece then the block hashes
                    # should be padded to the next power of two instead of the next
                    # piece boundary.
                    leaves_required = 1<<(len(blocks)-1).bit_length() if len(self.piecesv2) == 0 else blocks_per_piece
                    blocks.extend([bytes(32) for i in range(leaves_required - len(blocks))])
                self.piecesv2.append(root_hash(blocks))
                if residue > 0:
                    self.pad_length = residue
                    self.pad_hasher = v1hasher
                else:
                    self.piecesv1.append(v1hasher.digest())

        if self.length > 0:
            layer_hashes = self.piecesv2
            if len(self.piecesv2) > 1:
                # flatten piecesv2 into a single bytes object since that is what is needed for the 'piece layers' field
                self.piecesv2 = bytes([byte for piece in self.piecesv2 for byte in piece])
                # balance the tree by padding with zero hashes to the next power of two
                pad_piece_hash = root_hash([bytes(32)] * blocks_per_piece)
                layer_hashes.extend([pad_piece_hash for i in range((1<<(len(layer_hashes)-1).bit_length()) - len(layer_hashes))])
            self.root = root_hash(layer_hashes)

    def append_padding(self):
        self.pad_hasher.update(bytes(self.pad_length))
        return self.pad_hasher.digest()

    def discard_padding(self):
        return self.pad_hasher.digest()

class Torrent:
    def __init__(self, path, piece_length):
        assert piece_length >= BLOCK_SIZE
        assert piece_length & (piece_length - 1) == 0

        path = os.path.normpath(path)

        self.piece_length = piece_length
        self.name = os.path.basename(path)
        self.piece_layers = [] # v2 piece hashes
        self.pieces = [] # v1 piece hashes
        self.files = []
        self.info = []

        self.base_path = path

        if os.path.isfile(path):
            self.file_tree = {os.path.basename(path).encode(): self.walk_path(path)}
            delattr(self, 'files')
            self.length = self.file_tree[os.path.basename(path).encode()][b''][b'length']
        else:
            self.file_tree = self.walk_path(path)

        try:
            if hasattr(self, 'files') and len(self.files) > 1:
                self.pieces.append(self.residue_hasher.append_padding())
                self.files.append({b'attr': b'p', b'length': self.residue_hasher.pad_length, b'path': ['.pad', str(self.residue_hasher.pad_length)]})
            else:
                self.pieces.append(self.residue_hasher.discard_padding())
            delattr(self, 'residue_hasher')
        except AttributeError:
            assert not hasattr(self, 'residue_hasher') or not hasattr(self.residue_hasher, 'pad_hasher')

        # flatten the piece hashes into a single bytes object
        self.pieces = bytes([byte for piece in self.pieces for byte in piece])

        delattr(self, 'base_path')

    def walk_path(self, path):
        if os.path.isfile(path):
            try:
                self.pieces.append(self.residue_hasher.append_padding())
                self.files.append({b'attr': b'p', b'length': self.residue_hasher.pad_length, b'path': ['.pad', str(self.residue_hasher.pad_length)]})
                delattr(self, 'residue_hasher')
            except AttributeError:
                assert not hasattr(self, 'residue_hasher') or not hasattr(self.residue_hasher, 'pad_hasher')
            hashes = FileHasher(path, self.piece_length)
            self.residue_hasher = hashes
            self.piece_layers.append(hashes)
            self.pieces.extend(hashes.piecesv1)
            self.files.append({b'length': hashes.length, b'path': os.path.relpath(path, self.base_path).split(os.sep)})
            if hashes.length == 0:
                return {b'': {b'length': hashes.length}}
            else:
                return {b'': {b'length': hashes.length, b'pieces root': hashes.root}}
        if os.path.isdir(path):
            # the directory entries must be processed in lexicographic order so that
            # the files list matches the bencoded ordering of the file tree
            dentries = [(p.name.encode(), p.path) for p in os.scandir(path)]
            dentries.sort()
            return {p[0]: self.walk_path(p[1]) for p in dentries}

        raise ValueError('Unsupported dentry type')
              
    def create(self, tracker, hybrid=True):
        """
        Create a v2 metainfo dictionary.

        :param tracker: tracker URL
        :param hybrid: Also generate v1 fields for backwards compatibility
        """
        info = {b'name': self.name, b'piece length': self.piece_length, b'file tree':self.file_tree, b'meta version': 2}
        if hybrid:
            info[b'pieces'] = self.pieces
            try: info[b'files'] = self.files
            except AttributeError: info[b'length'] = self.length
        self.info = info
        return {b'announce': tracker, b'info': info, b'piece layers': {f.root: f.piecesv2 for f in self.piece_layers if f.length > self.piece_length}}

    def info_hash_v2(self):
        return sha256(encode(self.info)).hexdigest()

    def info_hash_v1(self):
        return sha1(encode(self.info)).hexdigest()


if __name__ == "__main__":
   import argparse
   parser = argparse.ArgumentParser(description='Bittorrent v2 metadata creator')
   parser.add_argument('path', help='The file or directory to build a torrent for')
   parser.add_argument('--piece-length', '-p', type=int, default=65536, help='Must be a power of two')
   parser.add_argument('--tracker', '-t', default='http://example.com/announce')
   parser.add_argument('--v2-only', '-2', action='store_false', help='Don\'t generate v1 compatibility keys')

   args = parser.parse_args()
   t = Torrent(args.path, args.piece_length)
   open(t.name + '.torrent', 'wb').write(encode(t.create(args.tracker, args.v2_only)))
   if args.v2_only:
       print("v1 infohash {0:s}".format(t.info_hash_v1()))
   print("v2 infohash {0:s}".format(t.info_hash_v2()))

