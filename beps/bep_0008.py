from sha import sha
from random import randint
from struct import unpack
#from rc4 import rc4              # generates RC4 psuedorandom string.

rand = open("/dev/random","r").read

class RC4:
  def __call__(self, i):
    return rand(i)

rc4 = RC4()                       # replace with actual RC4 implementation.

# tracker configuration
MAX_PEERS = 100

# per torrent state.
infohash = sha("dummy_info").digest()
pseudo = ''                        # pseudorandom RC-4 string.
num_peers = 1000                   # current swarm size.
tracker_peer_list = rand(6) * num_peers 
obfuscated_tracker_peer_list = '' 

def xor(plaintext,pseudo):
  isint = False
  if type(plaintext) == int: # convert to byte string.
    plaintext = "".join([chr(int(x,16)) for x in "%.4x" % plaintext])
    isint = True

  n = len(pseudo) 
    
  ciphertext = "".join( 
    [chr(ord(pseudo[i%n])^ord(plaintext[i])) for i in xrange(len(plaintext))] )

  if isint:
    ciphertext = unpack("!I", ciphertext)[0]   # convert back to unsigned int
  return ciphertext

def init():  # called once per rerequest interval.
  global iv, x, n, n_xor_y, obfuscated_tracker_peer_list
  iv = rand(20)
  rc4.key = sha(infohash + iv).digest()[0:8]
  rc4(768)                         # discard first 768
  x = rc4(4)
  y = rc4(4)
  n = min(num_peers, randint(MAX_PEERS * 2, MAX_PEERS * 4))
  n_xor_y = xor(n,y)
  pseudo = rc4(n*6)
  obfuscated_tracker_peer_list = xor(tracker_peer_list,pseudo)

def getpeers( numwant ):
  global iv, x, n, n_xor_y, obfuscated_tracker_peer_list
  response = {}
  response['iv'] = iv
  numwant = min(numwant, MAX_PEERS)
  if numwant >= num_peers:
    response['peers'] = obfuscated_tracker_peer_list
    return response

  i = randint(0,num_peers-numwant) 
  response['i'] = xor(i,x) 
  response['n'] = n_xor_y
  # peers at end of tracker peer list have lower probability of being picked,
  # but this requires only one copy.
  response['peers'] = obfuscated_tracker_peer_list[i*6:(i+numwant)*6]  
  return response 

init()
response = getpeers(20)
print "response=", response
print "len(response['peers'])=", len(response['peers'])
