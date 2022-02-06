import socket
from json import dumps, loads
from hashlib import sha3_256


class Client:  # Class formats and sends requests to the server, receives and decodes responses
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

    def __init__(self):  # Initialisation of connection with the server
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect((socket.gethostname(), 1234))

    def create_account(self, username, password, colours):  # Sending a request to create a user account
        colors_new = []
        for colour in colours:
            colors_new.append(dumps(colour))
        self.__client.send(bytes(self.CREATE_ACCOUNT +
                                 dumps((username, str(int.from_bytes(sha3_256(password.encode(self.ENCODING)).digest(),
                                                    "little")), colors_new)), self.ENCODING))  # Group A Skill, Hashing
        return loads(self.__client.recv(self.PACKET_SIZE).decode(self.ENCODING))

    def sign_in(self, username, password):  # Verifying provided user details for sign in
        self.__client.send(bytes(self.SIGN_IN +
                                 dumps((username, str(int.from_bytes(sha3_256(password.encode(self.ENCODING)).digest(),
                                                                     "little")))), self.ENCODING))  # Group A Skill, Hashing
        return loads(self.__client.recv(self.PACKET_SIZE).decode(self.ENCODING))

    def send_colours(self, username):
        self.__client.send(bytes(self.SEND_COLOURS + dumps(username), self.ENCODING))
        colours = []
        response = loads(self.__client.recv(self.PACKET_SIZE).decode(self.ENCODING))
        for colour in response:
            colours.append(loads(colour))
        return colours

    def update_colours(self, username, colours):
        colors_new = []
        for colour in colours:
            colors_new.append(dumps(colour))
        self.__client.send(bytes(self.UPDATE_COLOURS + dumps((username, colors_new)), self.ENCODING))

    def save_game(self, game_id, game_name, finished, player1, player2, game_sequence, meta_data):
        # Sending a request to store the game state with provided parameters
        game_sequence_str = ""
        for move in game_sequence:
            game_sequence_str += str(move)
        self.__client.send(bytes(self.SAVE_GAME + dumps((game_id, game_name, finished, player1, player2,
                                                         game_sequence_str, dumps(meta_data))), self.ENCODING))
        return loads(self.__client.recv(self.PACKET_SIZE).decode(self.ENCODING))

    def retrieve_game(self, game_id):  # Retrieving a specific game to continue play or review
        self.__client.send(bytes(self.RETRIEVE + dumps(game_id), self.ENCODING))
        result = loads(self.__client.recv(self.PACKET_SIZE).decode(self.ENCODING))
        return [result[0], loads(result[1])]

    def game_list(self, username, set_of_five_records, finished):
        # Retrieving a set of games played by a certain player
        self.__client.send(bytes(self.GAME_LIST + dumps((username, set_of_five_records * 5, finished)), self.ENCODING))
        return loads(self.__client.recv(self.PACKET_SIZE).decode(self.ENCODING))


if __name__ == '__main__':
    pass
