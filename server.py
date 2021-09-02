import socket
from json import dumps, loads, dump, load


class Server:
    CREATE_ACCOUNT = "ca"
    SIGN_IN = "si"

    def __init__(self):
        self.__procedure_list = {self.CREATE_ACCOUNT: self.__create_account, self.SIGN_IN: self.__sign_in}
        self.__user_information = None
        try:
            with open("Users.txt", "r") as file:
                self.__user_information = loads(file.read())
        except FileNotFoundError:
            with open("Users.txt", "w") as file:
                self.__user_information = {}
                dump(self.__user_information, file)
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((socket.gethostname(), 1234))
        self.__server.listen(10)
        self.__message_cycle()

    def __message_cycle(self):
        while True:
            client_socket, address = self.__server.accept()
            message = client_socket.recv(1024).decode("utf-8")
            self.__procedure_list[message[:2]](loads(message[2:]), client_socket, address)
            with open("Users.txt", "w") as file:
                dump(self.__user_information, file)

    def __create_account(self, arguments, client, address):
        username, password = arguments
        if username in self.__user_information:
            message = False
        else:
            message = True
            self.__user_information[username] = password
        client.send(bytes(dumps(message), "utf-8"))

    def __sign_in(self, arguments, client, address):
        username, password = arguments
        if username in self.__user_information:
            if self.__user_information[username] == password:
                message = 1
            else:
                message = 0
        else:
            message = -1
        client.send(bytes(dumps(message), "utf-8"))


if __name__ == '__main__':
    Server()