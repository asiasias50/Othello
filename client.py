import socket
from json import dumps, loads
from hashlib import sha3_256


class Client:  # Class formats and sends requests to the server, receives and decodes responses
    # Group A skill, Complex client-server model
    CREATE_ACCOUNT = "ca"
    SIGN_IN = "si"
    SAVE_GAME = "sg"
    RETRIEVE = "re"
    SHOW_PLAYED_GAMES = "spg"
    SEND_COLOURS = "sc"
    UPDATE_COLOURS = "uc"

    def __init__(self):  # Initialisation of connection with the server
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect((socket.gethostname(), 1234))

    def create_account(self, username, password, colours):  # Sending a request to create a user account
        colors_new = []
        for colour in colours:
            colors_new.append(dumps(colour))
        self.__client.send(bytes(self.CREATE_ACCOUNT +
                                 dumps((username, str(int.from_bytes(sha3_256(password.encode("utf-8")).digest(),
                                                    "little")), colors_new)), "utf-8"))  # Group A Skill, Hashing
        return loads(self.__client.recv(1024).decode('utf-8'))

    def sign_in(self, username, password):  # Verifying provided user details for sign in
        self.__client.send(bytes(self.SIGN_IN +
                                 dumps((username, str(int.from_bytes(sha3_256(password.encode("utf-8")).digest(),
                                                                     "little")))), "utf-8"))  # Group A Skill, Hashing
        return loads(self.__client.recv(1024).decode('utf-8'))

    def send_colours(self, username):
        self.__client.send(bytes(self.SEND_COLOURS + dumps(username), "utf-8"))
        colours = []
        response = loads(self.__client.recv(1024).decode('utf-8'))
        for colour in response:
            colours.append(loads(colour))
        return colours

    def update_colours(self, username, colours):
        colors_new = []
        for colour in colours:
            colors_new.append(dumps(colour))
        self.__client.send(bytes(self.UPDATE_COLOURS + dumps((username, colors_new)), "utf-8"))

    def save_game(self, puzzle, finished, player1_id, player2_id, game_sequence, starting_player):
        # Sending a request to store the game state with provided parameters
        game_sequence_str = ""
        if puzzle:
            game_sequence_str += starting_player
            for row in game_sequence:
                for col in row:
                    game_sequence_str += col
        else:
            for move in game_sequence:
                game_sequence_str += str(move[0]) + str(move[1])
        self.__client.send(bytes(self.SAVE_GAME + dumps((puzzle, finished, player1_id, player2_id, game_sequence_str)),
                                 "utf-8"))
        return loads(self.__client.recv(1024).decode('utf-8'))

    def retrieve_game(self, game_id):  # Retrieving a specific game to continue play or review
        self.__client.send(bytes(self.RETRIEVE + dumps(game_id), "utf-8"))
        return loads(self.__client.recv(1024).decode('utf-8'))

    def show_played_games(self, player_id):  # Retrieving a set of games played by a certain player
        self.__client.send(bytes(self.SHOW_PLAYED_GAMES + dumps(player_id), "utf-8"))
        return loads(self.__client.recv(1024).decode('utf-8'))


if __name__ == '__main__':
    c = Client()
    print(c.sign_in("Tom", "bbb"))
