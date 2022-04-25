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

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

parser = argparse.ArgumentParser(allow_abbrev=False, description="Upload a file to FTP Server")
parser.add_argument('--src', type=str, help='the source file name')
parser.add_argument('--dst', type=str, help='the destination file name')

args = parser.parse_args()
src = args.src if args.src else "soal1.py"
dst = args.dst if args.dst else src+".zip" if os.path.isdir(src) else src 

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
commands = ["USER " + USERNAME + SEPARATOR, 
    "PASS " + PASSWORD + SEPARATOR, 
    "TYPE I" + SEPARATOR, 
    "PASV" + SEPARATOR, 
    "STOR " + dst + SEPARATOR, 
    "QUIT" + SEPARATOR]

for i in range(len(commands)+1):
    try:
        message = client_socket.recv(BUFFER_SIZE).strip().decode()
        print(message)

        if "Entering Passive Mode" in message:
            result = re.search(r"([0-9]*),([0-9]*)\)", message)
            p1, p2 = int(result.group(1)), int(result.group(2))
            data_port = (p1*256) + p2            
            data_socket.connect((HOST, data_port)) 
        elif "Starting data transfer" in message:
            if os.path.isfile(src):
                with open(src, "rb") as file:
                    content = file.read()
                    data_socket.sendall(content)
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
            else:
                print("File not found, upload empty file..")
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