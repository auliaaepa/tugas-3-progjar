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

def create_data_socket():
    # send PASV command
    client_socket.send("PASV{}".format(SEPARATOR).encode())
    time.sleep(1) 

    # receive message
    message = client_socket.recv(BUFFER_SIZE).strip().decode()
    # calculate the new data port
    result = re.search(r"([0-9]*),([0-9]*)\)", message)
    p1, p2 = int(result.group(1)), int(result.group(2))
    data_port = (p1*256) + p2
    # connect to the new data port
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((HOST, data_port))
    
    return data_socket

def listdir(path): 
    # send PASV command and receive message
    client_socket.send("CWD {}{}".format(path, SEPARATOR).encode())
    time.sleep(1) 
    client_socket.recv(BUFFER_SIZE)

    # create data socket
    data_socket = create_data_socket()

    # send MLSD command and receive message
    client_socket.send("MLSD{}".format(SEPARATOR).encode())
    time.sleep(1) 
    client_socket.recv(BUFFER_SIZE)

    # receive list
    data = data_socket.recv(BUFFER_SIZE).strip().decode()
    data_list = data.split(SEPARATOR)
    data_socket.close()
    # collect file and dir name
    dirs, files = [], []
    for i in range(len(data_list)):
        result = re.search(r"type=([a-zA-Z]*);.*; (.*)", data_list[i])
        if result:
            ftype, name = result.group(1), result.group(2)
            if ftype == "dir":
                dirs.append(name)
            elif ftype == "file":
                files.append(name)

    return dirs, files

def walk(path):
    dirs, files = listdir(path)
    yield path, dirs, files
    for dir in dirs:
        # send PWD command and receive message
        client_socket.send("PWD{}".format(SEPARATOR).encode())
        time.sleep(1)
        message = client_socket.recv(BUFFER_SIZE).strip().decode()
        
        path = message.split("\"")[1] + "/" + dir
        yield from walk(path)

        client_socket.send("CWD ..{}".format(SEPARATOR).encode())
        time.sleep(1) 
        message = client_socket.recv(BUFFER_SIZE).strip().decode()

def main():
    # define command list
    dir = "/test2"
    commands = ["USER " + USERNAME + SEPARATOR, 
        "PASS " + PASSWORD + SEPARATOR, 
        "RMD " + dir + SEPARATOR, 
        "QUIT" + SEPARATOR]
    
    for i in range(len(commands)+1):
        try:
            # receive message
            message = client_socket.recv(BUFFER_SIZE).strip().decode()
            print(message)

            # send command
            if i < len(commands):
                if "RMD" in commands[i]:
                    dirpaths, filepaths = [], []
                    for root, dirs, files in walk(dir):
                        for dir in dirs:
                            dirpaths.append(root + "/" + dir)
                        for file in files:
                            filepaths.append(root + "/" + file)
                    for filepath in filepaths[::-1]:
                        # send DELE command and receive message
                        client_socket.send("DELE {}{}".format(filepath, SEPARATOR).encode())
                        time.sleep(1) 
                        message = client_socket.recv(BUFFER_SIZE).strip().decode()
                        # print(message)
                    for dirpath in dirpaths[::-1]:
                        # send RMD command and receive message
                        client_socket.send("RMD {}{}".format(dirpath, SEPARATOR).encode())
                        time.sleep(1) 
                        message = client_socket.recv(BUFFER_SIZE).strip().decode()
                        # print(message)
                
                client_socket.send(commands[i].encode()) 
                # print("\n>> " + commands[i].strip()) 

            # wait until process done
            time.sleep(1) 
        
        except socket.error:
            print("SOCKET ERROR")
            break

    client_socket.close()

if __name__ == "__main__":
    main()