import socket
from json import dumps, loads
import mysql.connector


class Server:
    CREATE_ACCOUNT = "ca"
    SIGN_IN = "si"

    def __init__(self):
        self.__procedure_list = {self.CREATE_ACCOUNT: self.__create_account, self.SIGN_IN: self.__sign_in}
        self.__database = self.__connect_to_database()
        self.__cursor = self.__database.cursor()
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((socket.gethostname(), 1234))
        self.__server.listen(10)
        self.__message_cycle()

    def __connect_to_database(self):
        database_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="jnBXXxggv&E9E!?N",
            database="othello"
        )
        return database_connection

    def __message_cycle(self):
        while True:
            client_socket, address = self.__server.accept()
            message = client_socket.recv(1024).decode("utf-8")
            self.__procedure_list[message[:2]](loads(message[2:]), client_socket, address)

    def __create_account(self, arguments, client, address):
        username, password = arguments
        self.__cursor.execute(f'SELECT COUNT(USERNAME) FROM user_information WHERE USERNAME = "{username}"')
        if self.__cursor.fetchall()[0][0] > 0:
            message = False
        else:
            message = True
            self.__cursor.execute(f'INSERT INTO user_information (USERNAME, PASSWORD) VALUES ("{username}", "{password}")')
            self.__database.commit()
        client.send(bytes(dumps(message), "utf-8"))

    def __sign_in(self, arguments, client, address):
        username, password = arguments
        self.__cursor.execute(f'SELECT COUNT(USERNAME) FROM user_information WHERE USERNAME = "{username}"')
        if self.__cursor.fetchall()[0][0] > 0:
            self.__cursor.execute(f'SELECT PASSWORD FROM user_information WHERE USERNAME = "{username}"')
            if self.__cursor.fetchall()[0][0] == password:
                message = 1
            else:
                message = 0
        else:
            message = -1
        client.send(bytes(dumps(message), "utf-8"))


if __name__ == '__main__':
    Server()