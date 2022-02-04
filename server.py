import socket
from json import dumps, loads
import mysql.connector


class Server:  # Class acts as a stand alone application, retrieving requests from clients,
    # quering requests to the MySQL database and sending appropriate responces
    # Group A skill, Complex client-server model
    CREATE_ACCOUNT = "ca"
    SIGN_IN = "si"
    SAVE_GAME = "sg"
    RETRIEVE = "re"
    SHOW_PLAYED_GAMES = "spg"
    SEND_COLOURS = "sc"
    UPDATE_COLOURS = "uc"

    def __init__(self):
        self.__procedure_list = {self.CREATE_ACCOUNT: self.__create_account, self.SIGN_IN: self.__sign_in,
                                 self.SAVE_GAME: self.__save_game, self.RETRIEVE: self.__retrieve_game,
                                 self.SHOW_PLAYED_GAMES: self.__show_played_games,
                                 self.SEND_COLOURS: self.__send_colours,
                                 self.UPDATE_COLOURS: self.__update_colours}
        # Establishing connection with MySQL database
        # Group A skill, Server-side extension
        self.__database = self.__connect_to_database()
        self.__cursor = self.__database.cursor()
        # Setting a server to listen to a particular port for incoming requests
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind((socket.gethostname(), 1234))
        self.__server.listen(10)
        self.__message_cycle()

    def __connect_to_database(self):  # Connection and sign in for MySQL database, local to the server
        database_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="w%y$*PY73kdv7Eqp",
            database="othello"
        )
        return database_connection

    def __message_cycle(self):  # Listening and processing cycle for clients' requests
        while True:
            client_socket, address = self.__server.accept()
            message = client_socket.recv(1024).decode("utf-8")
            if message != "":
                self.__procedure_list[message[:2]](loads(message[2:]), client_socket)

    def __create_account(self, arguments, client):  # Querying MySQL database to create new user account
        username, password, colours = arguments
        self.__cursor.execute(f'SELECT COUNT(USERNAME) FROM user_information WHERE USERNAME = "{username}"')
        # Group A skill, Aggregate SQL functions
        if self.__cursor.fetchall()[0][0] > 0:
            message = False
        else:
            message = True
            self.__cursor.execute(f'INSERT INTO user_information (USERNAME, PASSWORD_HASH, FIRST_PLAYER_COLOUR, '
                                  f'SECOND_PLAYER_COLOUR, BOARD_COLOUR) VALUES '
                                  f'("{username}", "{password}", "{colours[0]}", "{colours[1]}", "{colours[2]}")')
            self.__database.commit()
        client.send(bytes(dumps(message), "utf-8"))

    def __sign_in(self, arguments, client):  # Querying MySQL database to check the validity of user details for sign in
        username, password = arguments
        self.__cursor.execute(f'SELECT COUNT(USERNAME) FROM user_information WHERE USERNAME = "{username}"')
        # Group A skill, Aggregate SQL functions
        if self.__cursor.fetchall()[0][0] > 0:
            self.__cursor.execute(f'SELECT PASSWORD_HASH FROM user_information WHERE USERNAME = "{username}"')
            if self.__cursor.fetchall()[0][0] == password:
                message = 1
            else:
                message = 0
        else:
            message = -1
        client.send(bytes(dumps(message), "utf-8"))

    def __send_colours(self, arguments, client):
        username = arguments
        self.__cursor.execute(f'SELECT FIRST_PLAYER_COLOUR, SECOND_PLAYER_COLOUR, BOARD_COLOUR '
                              f'FROM user_information WHERE USERNAME = "{username}"')
        message = self.__cursor.fetchall()[0]
        client.send(bytes(dumps(message), "utf-8"))

    def __update_colours(self, arguments, client):
        username, colours = arguments
        self.__cursor.execute(f'UPDATE user_information SET FIRST_PLAYER_COLOUR = "{colours[0]}",'
                              f'SECOND_PLAYER_COLOUR = "{colours[1]}", BOARD_COLOUR = "{colours[2]}"'
                              f'WHERE USERNAME = "{username}"')
        self.__database.commit()
        client.send(bytes(dumps(True), "utf-8"))

    def __save_game(self, arguments, client):
        # Querying either an update to existing game save or to create a new entry for game save
        puzzle, finished, player1_id, player2_id, game_sequence_str = arguments
        if player2_id is None:
            player2_id = "NULL"
        else:
            player2_id = f'"{player2_id}"'
        self.__cursor.execute(f'SELECT game_id FROM games_played WHERE player1_id = "{player1_id}"'
                              f' AND player2_id = {player2_id}')
        game_id = self.__cursor.fetchall()
        if len(game_id) > 0:
            self.__cursor.execute(f'UPDATE game_information SET finished = "{int(finished)}",'
                                  f' game_sequence = {game_sequence_str} WHERE game_id = {game_id[0][0]}')
        else:
            self.__cursor.execute(f'INSERT INTO game_information (player1_id, player2_id)'
                                  f' VALUES ("{puzzle}", "{finished}", "{game_sequence_str}")')
            self.__cursor.execute(f'INSERT INTO games_played (player1_id, player2_id)'
                                  f' VALUES ("{player1_id}", {player2_id})')
        self.__database.commit()
        client.send(bytes(dumps(True), "utf-8"))

    def __retrieve_game(self, arguments, client):
        game_id = arguments[0]
        self.__cursor.execute(f'SELECT game_sequence FROM game_information WHERE game_id = {game_id}')
        message = self.__cursor.fetchall()[0][0]
        client.send(bytes(dumps(message), "utf-8"))

    def __show_played_games(self, arguments, client):
        player_id = arguments[0]
        # Group A skill, Aggregate SQL functions
        self.__cursor.execute(f'SELECT * FROM game_information INNER JOIN games_played ON'
                              f' game_information.game_id = games_played.game_id '
                              f'WHERE player1_id = "{player_id}" OR player2_id = "{player_id}" ORDER BY game_id DESC')
        message = self.__cursor.fetchall()
        client.send(bytes(dumps(message), "utf-8"))


if __name__ == '__main__':
    Server()
