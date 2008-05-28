import socket

tlds = ["com", "net", "org"]  # add more here.

name, aliases, ipaddrs = socket.gethostbyaddr("69.107.0.14")
names = name.split('.')
while names and names[0] not in tlds:
   name = "bittorrent-tracker." + ".".join(names)
   try:
     print "looking up name ", name
     ip = socket.gethostbyname(name)
     break
   except:
     del names[0]

print "response=", ip

