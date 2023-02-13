import socket 
import select
import sys 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.connect(("65.112.8.17", 6000))

while True:
    sockets_list = [sys.stdin, server]

server.close()
