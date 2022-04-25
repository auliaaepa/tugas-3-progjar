import socket
import time

BUFFER_SIZE = 4096
SEPARATOR = "\r\n"
HOST = "localhost"
PORT = 21
USERNAME = "aulia"
PASSWORD = "aulia123"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

commands = ["USER " + USERNAME + SEPARATOR, 
    "PASS " + PASSWORD + SEPARATOR, 
    "RMD test2" + SEPARATOR, 
    "QUIT" + SEPARATOR]

for i in range(len(commands)+1):
    try:
        message = client_socket.recv(BUFFER_SIZE).strip().decode()
        print(message)

        if i < len(commands):
            client_socket.send(commands[i].encode()) 
            print("\n>> " + commands[i].strip()) 

        time.sleep(1) 
    
    except socket.error:
        print("SOCKET ERROR")
        break

client_socket.close()