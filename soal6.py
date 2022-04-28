import socket
import time

BUFFER_SIZE = 4096
SEPARATOR = "\r\n"
HOST = "localhost"
PORT = 21
USERNAME = "aulia"
PASSWORD = "aulia123"

# connect to ftp server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# define command list
commands = ["USER " + USERNAME + SEPARATOR, 
    "PASS " + PASSWORD + SEPARATOR, 
    "PWD" + SEPARATOR, 
    "QUIT" + SEPARATOR]

for i in range(len(commands)+1):
    try:
        # receive message
        message = client_socket.recv(BUFFER_SIZE).strip().decode()
        print(message)

        # send command
        if i < len(commands):
            client_socket.send(commands[i].encode()) 
            # print("\n>> " + commands[i].strip()) 

        # wait until process done
        time.sleep(1) 
    
    except socket.error:
        print("SOCKET ERROR")
        break

client_socket.close()