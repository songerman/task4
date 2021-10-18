import socket
import dnslib

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.sendto(dnslib.DNSRecord.question("google.com").pack(), ('localhost', 53))
server.close()
