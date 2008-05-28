# Uses PyDNS.

import DNS

#req = DNS.Request( name="www.google.com", qtype="A", protocol= "udp", server="10.211.55.3" )
#req = DNS.Request( name="www.google.com", qtype="A", protocol= "udp", server="127.0.0.1" )
#req = DNS.Request( name="www.google.com", qtype="A", protocol= "udp", server="localhost" )
#print "www.google.com: ", req.req().show()

tlds = ["com", "net", "org"]  # add more here.

name = DNS.revlookup( "77.46.197.147" )
names = name.split('.')
while names and names[0] not in tlds:
   name = "_bittorrent._tcp." + ".".join(names)
   req = DNS.Request( name=name, qtype="SRV", protocol="udp", server="localhost") 
   response = req.req()
   if response.answers:
      break
   del names[0]

print "response=", response.show()   


