import socket
import re, time
import argparse
import os, zipfile

BUFFER_SIZE = 4096
SEPARATOR = "\r\n"
HOST = "localhost"
PORT = 21
USERNAME = "aulia"
PASSWORD = "aulia123"

# connect to ftp server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# initialize argument parser to customize src and dst file path
parser = argparse.ArgumentParser(allow_abbrev=False, description="Upload a file to FTP Server")
parser.add_argument('--src', type=str, help='the source path')
parser.add_argument('--dst', type=str, help='the destination path')

# get arguments and define src and dst file path
args = parser.parse_args()
src = args.src if args.src else "soal1.py"
dst = args.dst+".zip" if args.dst and os.path.isdir(src) and ".zip" not in args.dst else \
    args.dst if args.dst and ((os.path.isdir(src) and ".zip" in args.dst) or os.path.isfile(src)) else \
    os.path.basename(src)+".zip" if os.path.isdir(src) else \
    os.path.basename(src) 
# print(os.path.exists(src), src, dst)

# initilize data socket for data transfer
data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# define command list
commands = ["USER " + USERNAME + SEPARATOR, 
    "PASS " + PASSWORD + SEPARATOR, 
    "TYPE I" + SEPARATOR, 
    "PASV" + SEPARATOR, 
    "STOR " + dst + SEPARATOR, 
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
            data_socket.connect((HOST, data_port)) 
        # if STOR command's successful,
        elif "Starting data transfer" in message:
            # send file content if it's file
            if os.path.isfile(src):
                with open(src, "rb") as file:
                    content = file.read()
                    data_socket.sendall(content)
            # send zipped directory if it's directory
            elif os.path.isdir(src):
                with zipfile.ZipFile(src+".zip", "w", zipfile.ZIP_DEFLATED) as zip:
                    for root, dirs, files in os.walk(src):
                        for file in files:
                            zip.write(os.path.join(root, file), 
                                    os.path.relpath(os.path.join(root, file), os.path.join(src, '..')))
                with open(src+".zip", "rb") as file:
                    content = file.read()
                    data_socket.sendall(content)
                os.remove(src+".zip")
            # # empty file's created if it doesn't exist
            # else:
            #     print("File not found, upload empty file..")
            
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