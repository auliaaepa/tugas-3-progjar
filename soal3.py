import socket
import re, time

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
    "PASV" + SEPARATOR, 
    "MLSD" + SEPARATOR, 
    "QUIT" + SEPARATOR]

for i in range(len(commands)+1):
    try:
        # receive message
        message = client_socket.recv(BUFFER_SIZE).strip().decode()
        print(message)

        # if PASV command's successful,
        if "Entering Passive Mode" in message:
            # calculate the new data port
            result = re.search(r"([0-9]*),([0-9]*)\)", message)
            p1, p2 = int(result.group(1)), int(result.group(2))
            data_port = (p1*256) + p2
            # connect to the new data port
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((HOST, data_port))
        # if MLSD command's successful,
        elif "Starting data transfer" in message:
            # get list
            data = data_socket.recv(BUFFER_SIZE).strip().decode()
            data_list = data.split(SEPARATOR)
            # find file/dir name and display it
            for j in range(len(data_list)):
                result = re.search(r"; (.*)", data_list[j])
                if result:
                    filename = result.group(1)
                    print(filename)
            # close data socket to continue to the next command (end pasv mode)
            data_socket.close()

        # send command
        if i < len(commands):
            client_socket.send(commands[i].encode()) 
            # print("\n>> " + commands[i].strip())

        # wait until process done
        time.sleep(1)

    except socket.error:
        print("SOCKET ERROR")
        break

    except AttributeError:
        print("ATTRIBUTE ERROR")
        break

client_socket.close()