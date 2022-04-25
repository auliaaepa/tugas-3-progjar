import socket
import re, time

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
    "PASV" + SEPARATOR, 
    "MLSD" + SEPARATOR, 
    "QUIT" + SEPARATOR]

for i in range(len(commands)+1):
    try:
        message = client_socket.recv(BUFFER_SIZE).strip().decode()
        print(message)

        if "Entering Passive Mode" in message:
            result = re.search(r"([0-9]*),([0-9]*)\)", message)
            p1, p2 = int(result.group(1)), int(result.group(2))
            data_port = (p1*256) + p2
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((HOST, data_port))
        elif "Starting data transfer" in message:
            data = data_socket.recv(BUFFER_SIZE).strip().decode()
            data_list = data.split(SEPARATOR)
            # print(data_list)
            for j in range(len(data_list)):
                result = re.search(r"; (.*)", data_list[j])
                if result:
                    filename = result.group(1)
                    print(filename)
            data_socket.close()
        
        if i < len(commands):
            client_socket.send(commands[i].encode()) 
            # print("\n>> " + commands[i].strip())

        time.sleep(1)

    except socket.error:
        print("SOCKET ERROR")
        break

    except AttributeError:
        print("ATTRIBUTE ERROR")
        break

client_socket.close()