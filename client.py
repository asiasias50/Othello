import socket
from json import dumps, loads


class Client:
    CREATE_ACCOUNT = "ca"
    SIGN_IN = "si"

    def __init__(self):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect((socket.gethostname(), 1234))

    def create_account(self, username, password):
        self.__client.send(bytes(self.CREATE_ACCOUNT + dumps((username, password)), "utf-8"))
        return loads(self.__client.recv(1024).decode('utf-8'))

    def sign_in(self, username, password):
        self.__client.send(bytes(self.SIGN_IN + dumps((username, password)), "utf-8"))
        return loads(self.__client.recv(1024).decode('utf-8'))


if __name__ == '__main__':
    c = Client()
    print(c.sign_in("sum", "yyyIII"))