import socket
from json import dumps, loads
import mysql.connector


class Server:  # Class acts as a stand alone application, retrieving requests from clients,
    # quering requests to the MySQL database and sending appropriate responces
    # Group A skill, Complex client-server model
    PACKET_SIZE = 4096
    ENCODING = "utf-8"
    CREATE_ACCOUNT = "ca"
    SIGN_IN = "si"
    SAVE_GAME = "sg"
    RETRIEVE = "re"
    GAME_LIST = "gl"
    SEND_COLOURS = "sc"
    UPDATE_COLOURS = "uc"
    ARCHIVE = "ar"
    RATING = "ra"

    def __init__(self):
        self.__procedure_list = {self.CREATE_ACCOUNT: self.__create_account, self.SIGN_IN: self.__sign_in,
                                 self.SAVE_GAME: self.__save_game, self.RETRIEVE: self.__retrieve_game,
                                 self.GAME_LIST: self.__game_list,
                                 self.SEND_COLOURS: self.__send_colours,
                                 self.UPDATE_COLOURS: self.__update_colours,
                                 self.ARCHIVE: self.__archive,
                                 self.RATING: self.__rating}
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
            message = client_socket.recv(self.PACKET_SIZE).decode(self.ENCODING)
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
        client.send(bytes(dumps(message), self.ENCODING))

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
        client.send(bytes(dumps(message), self.ENCODING))

    def __send_colours(self, arguments, client):
        username = arguments
        self.__cursor.execute(f'SELECT FIRST_PLAYER_COLOUR, SECOND_PLAYER_COLOUR, BOARD_COLOUR '
                              f'FROM user_information WHERE USERNAME = "{username}"')
        message = self.__cursor.fetchall()[0]
        client.send(bytes(dumps(message), self.ENCODING))

    def __update_colours(self, arguments, client):
        username, colours = arguments
        self.__cursor.execute(f'UPDATE user_information SET FIRST_PLAYER_COLOUR = "{colours[0]}",'
                              f'SECOND_PLAYER_COLOUR = "{colours[1]}", BOARD_COLOUR = "{colours[2]}"'
                              f'WHERE USERNAME = "{username}"')
        self.__database.commit()
        client.send(bytes(dumps(True), self.ENCODING))

    def __save_game(self, arguments, client):
        # Querying either an update to existing game save or to create a new entry for game save
        game_id, game_name, finished, player1, player2, game_sequence_str, meta_data_str = arguments
        if game_id == "NULL":
            self.__cursor.execute(f'SELECT player_id FROM user_information WHERE username = "{player1}"')
            player1_id = self.__cursor.fetchall()[0][0]
            if player2 != "NULL":
                self.__cursor.execute(f'SELECT player_id FROM user_information WHERE username = "{player2}"')
                player2_id = f'"{self.__cursor.fetchall()[0][0]}"'
            else:
                player2_id = 0
            self.__cursor.execute(f'INSERT INTO game_information (finished, game_sequence, meta_data)'
                                  f' VALUES ("{int(finished)}", "{game_sequence_str}", "{meta_data_str}")')
            self.__cursor.execute(f'INSERT INTO games_played (player1_id, player2_id, game_name)'
                                  f' VALUES ("{player1_id}", {player2_id}, "{game_name}")')
            if int(finished) > 0 and player2 != "NULL":
                if int(finished) == 1:
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player1_id}"')
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET total = total + 1, rating = wins / total'
                                          f' WHERE player_id = {player2_id}')
                elif int(finished) == 2:
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player1_id}"')
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = {player2_id}')
                else:
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player1_id}"')
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = {player2_id}')
        else:
            self.__cursor.execute(f'UPDATE game_information SET finished = "{int(finished)}",'
                                  f' game_sequence = "{game_sequence_str}", meta_data = "{meta_data_str}"'
                                  f' WHERE game_id = "{game_id}"')
            self.__cursor.execute(f'SELECT player1_id FROM games_played WHERE game_id = "{game_id}"')
            player1_id = self.__cursor.fetchall()[0][0]
            self.__cursor.execute(f'SELECT player2_id FROM games_played WHERE game_id = "{game_id}"')
            player2_id = self.__cursor.fetchall()[0][0]
            if int(finished) > 0 and player2 != 0:
                if int(finished) == 1:
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player1_id}"')
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player2_id}"')
                elif int(finished) == 2:
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player1_id}"')
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player2_id}"')
                else:
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player1_id}"')
                    self.__cursor.execute(f'UPDATE user_information '
                                          f'SET wins = wins + 1, total = total + 1, rating = wins / total'
                                          f' WHERE player_id = "{player2_id}"')
        self.__database.commit()
        client.send(bytes(dumps(True), self.ENCODING))

    def __retrieve_game(self, arguments, client):
        game_id = arguments
        self.__cursor.execute(f'SELECT game_sequence, meta_data FROM game_information WHERE game_id = {game_id}')
        message = self.__cursor.fetchall()[0]
        client.send(bytes(dumps(message), self.ENCODING))

    def __game_list(self, arguments, client):
        username, set_of_five_records, finished = arguments
        self.__cursor.execute(f'SELECT player_id FROM user_information WHERE username = "{username}"')
        username = self.__cursor.fetchall()[0][0]
        # Group A skill, Aggregate SQL functions
        self.__cursor.execute(f'SELECT games_played.game_id, games_played.player2_id, games_played.game_name '
                              f'FROM games_played INNER JOIN game_information ON'
                              f' games_played.game_id = game_information.game_id '
                              f'WHERE games_played.player1_id = "{username}" AND '
                              f'game_information.finished = "{int(finished)}"'
                              f'ORDER BY games_played.game_id DESC')
        game_names_and_IDs = self.__cursor.fetchall()[0 + set_of_five_records:5 + set_of_five_records]
        result = []
        for record in game_names_and_IDs:
            result_per_record = []
            result_per_record.append(record[0])
            if record[1] == 0:
                result_per_record.append("AI")
            else:
                self.__cursor.execute(f'SELECT username FROM user_information WHERE player_id = {record[1]}')
                result_per_record.append(self.__cursor.fetchall()[0][0])
            result_per_record.append(record[2])
            result.append(result_per_record)
        client.send(bytes(dumps(result), self.ENCODING))

    def __archive(self, arguments, client):
        set_of_five_records, username = arguments
        if username is None:
            self.__cursor.execute(f'SELECT games_played.game_name, games_played.player1_id, games_played.player2_id, '
                                  f'game_information.finished, games_played.game_id '
                                  f'FROM games_played INNER JOIN game_information ON'
                                  f' games_played.game_id = game_information.game_id '
                                  f'WHERE game_information.finished != "{0}"'
                                  f'ORDER BY games_played.game_id DESC')
        else:
            self.__cursor.execute(f'SELECT player_id FROM user_information WHERE username = "{username}"')
            username = self.__cursor.fetchall()[0][0]
            self.__cursor.execute(f'SELECT games_played.game_name, games_played.player1_id, games_played.player2_id, '
                                  f'game_information.finished, games_played.game_id '
                                  f'FROM games_played INNER JOIN game_information ON'
                                  f' games_played.game_id = game_information.game_id '
                                  f'WHERE game_information.finished != "{0}"'
                                  f'AND (games_played.player1_id = "{username}" OR'
                                  f' games_played.player2_id = "{username}")'
                                  f'ORDER BY games_played.game_id DESC')
        game_names_and_IDs = self.__cursor.fetchall()[0 + set_of_five_records:5 + set_of_five_records]
        result = []
        for record in game_names_and_IDs:
            result_per_record = []
            result_per_record.append(record[0])
            self.__cursor.execute(f'SELECT username FROM user_information WHERE player_id = {record[1]}')
            result_per_record.append(self.__cursor.fetchall()[0][0])
            if record[2] == 0:
                result_per_record.append("AI")
            else:
                self.__cursor.execute(f'SELECT username FROM user_information WHERE player_id = {record[2]}')
                result_per_record.append(self.__cursor.fetchall()[0][0])
            result_per_record.append(record[3])
            result_per_record.append(record[4])
            result.append(result_per_record)
        client.send(bytes(dumps(result), self.ENCODING))

    def __rating(self, arguments, client):
        set_of_five_records = arguments
        self.__cursor.execute(f'SELECT username, wins, total, rating FROM user_information ORDER BY rating DESC')
        player_info = self.__cursor.fetchall()[0 + set_of_five_records:5 + set_of_five_records]
        client.send(bytes(dumps(player_info), self.ENCODING))


if __name__ == '__main__':
    Server()
