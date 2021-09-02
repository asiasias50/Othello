import socket
from json import dumps, loads

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 1234))

user = "ty"
password = "0987"

client.send(bytes("qs" + dumps((user, password)), "utf-8"))
