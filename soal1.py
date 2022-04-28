import socket
import re

BUFFER_SIZE = 4096
SEPARATOR = "\r\n"
HOST = "localhost"
PORT = 21

# connect to ftp server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# receive welcome message
message = client_socket.recv(BUFFER_SIZE).strip().decode()

# get ftp server name and version
message_list = message.split(SEPARATOR)
result = re.search(r"\b([0-9]*)-\b(.*)", message_list[0])
ftp_host = result.group(2)
print(ftp_host)

client_socket.close()