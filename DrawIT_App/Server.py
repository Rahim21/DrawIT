import random
import socket
import select
import os
from pathlib import Path
import pickle
import ast

def cleanTerminal():  # Clears the terminal on Linux, Mac & Windows.
    if (os.name == "posix"):
        os.system("clear")
    # elif (platform.system() == "Windows"):
    else:
        os.system("cls")


connections = []
player_list_Names: dict[int, str] = {}
score_list: dict[str, dict] = {}
buffer = 1024
serverIP = "127.0.0.1"
# port = random.randrange(9000,9999)
port = 5555
serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSock.bind((serverIP, port))
serverSock.listen(15)
connections.append(serverSock)
global addr

# Drawing time
game_duration = input("Drawing duration (in seconds): ")
while not game_duration.isdigit() or int(game_duration) < 20:
    game_duration = input("Enter a valid number (20 or more): ")
the_game_duration = int(game_duration)


# Number of game turn
game_turn = input("Number of game turn: ")
while not game_turn.isdigit() or int(game_turn) < 1:
    game_turn = input("Enter a valid number > 0: ")
the_game_turn = int(game_turn)

iteratePlayer = 0
select_player_id = None

cleanTerminal()
print(f"The game server is now live at {serverIP} on port {port}")


class HiddenWord(object):
    def __init__(self):
        self.theRandomWord = None
        self.theOldWord = None
        self.theWord = None

    def newWord(self):
        word_file = Path(__file__).parent / Path("./assets/mots.txt")
        with open(word_file, "r") as file:
            data = file.read()
            words = data.split()
            word_pos = random.randint(0, len(words)-1)
            self.theNewWord = words[word_pos]
            self.theOldWord = self.theNewWord
        return self.theNewWord

    def oldWord(self):
        if self.theOldWord == None:
            self.newWord()
        else:
            return self.theOldWord


the_word = HiddenWord()


def wordIsCorrect(msgValue):
    # Making it case-insensitive and eliminating trailing whitspaces.
    oldWord = the_word.oldWord()
    theWord = str(oldWord).strip().upper().lower()

    msgValue = msgValue.strip().upper().lower()

    if msgValue == theWord:
        return True
    return False


def drawerTurn():
    # parcours le tableau de joueur et récupère l'id de chacun
    global iteratePlayer, the_game_turn, select_player_id
    # revenir au premier joueur si on est au dernier (PLUS TARD : si il reste des tours sinon FIN DU JEU)
    while the_game_turn > 0:
        if iteratePlayer >= len(player_list_Names):
            iteratePlayer = 0
            the_game_turn -= 1
        if the_game_turn <= 0:
            continue
        select_player_id = list(player_list_Names.keys())[
            iteratePlayer]
        print(select_player_id)
        return select_player_id
    print("END OF GAME")


def msgInterpreter(data, sock):
    # Incoming messages from the game client are structured differently depending on their purpose.
    # Common for most of them is the inclusion of "//" as a data divider.
    theWord = the_word.oldWord()
    msgParts = data.decode().strip().split("//")
    global iteratePlayer, the_game_turn
    # All message types, except for Word Guesses, are made out of 2 elements.
    if len(msgParts) == 2:
        msgType = msgParts[0]
        msgValue = msgParts[1]

        if len(msgType) < 1:
            msgType = "//"
            print(
                f"Msg recognized as chat message from player {player_list_Names[sock.fileno()]}")
            if msgValue == "CHEAT":
                # send the hidden word to the player
                data = f"CHEAT:{sock.fileno()}:{theWord}"
            elif msgValue == "START":
                # send a new generated word to the client
                # faire autre chose toute les initialisation d'un début de partie
                theWord = the_word.newWord()
                playerTurn = drawerTurn()
                # send the player turn id and the word to initialize the game
                initializeGame = [theWord, str(
                    playerTurn), int(the_game_duration)]
                data = f"START_GAME:{player_list_Names[sock.fileno()]}:{initializeGame}"
                # score_list mettre pour chaque joueur un score de 0 par défaut
                for user in player_list_Names:
                    score_list[str(user)] = {
                        "USERNAME": player_list_Names[user], "SCORE": "0"}
                pickle.dump(score_list, open("leaderboard_data.p", "wb"))
            elif msgValue == "NEW_WORD":
                theWord = the_word.newWord()
                iteratePlayer += 1
                playerTurn = drawerTurn()
                # send the new player turn id and the new generated word
                new_round_data = [theWord, str(
                    playerTurn), int(the_game_duration)]
                if the_game_turn > 0:
                    data = f"NEW_WORD:{player_list_Names[sock.fileno()]}:{new_round_data}"
                else:
                    data = f"END_GAME:{player_list_Names[sock.fileno()]}:END"
            else:
                data = f"{msgType}:{player_list_Names[sock.fileno()]}:{msgValue.strip()}"
            data = data.encode()

        if msgType == "NEW_PLAYER":
            print("Msg recognized as Set Name command)")
            player_list_Names[sock.fileno()] = msgValue
            totPlayers = len(player_list_Names)
            print(
                f"Received player name for player ID {sock.fileno()}: {player_list_Names[sock.fileno()]}")
            broadcast(sock, "{} has joined the game, making you a total of {} people!".format(
                msgValue, totPlayers))
            data = f"PLAYER_ID:{player_list_Names[sock.fileno()]}:{sock.fileno()}"
            data = data.encode()

        if msgType == "SCORE":
            print("Msg recognized as Score command)")
            score_data = ast.literal_eval(msgValue)
            # Player who answer score
            score_list[str(sock.fileno())
                       ]["USERNAME"] = player_list_Names[sock.fileno()]
            score_list[str(sock.fileno())]["SCORE"] = score_data[0]

            # Player who draw score
            score_list[str(select_player_id)]["SCORE"] = str(int(score_list[str(select_player_id)]["SCORE"])+int(score_data[1]))

            data = f"SCORE:{player_list_Names[sock.fileno()]}:SCORE_DUMPED"

            pickle.dump(score_list, open("leaderboard_data.p", "wb"))
            data = data.encode()

        if msgType == "FRAME_LINE":
            print(
                f"Frame painted by player {player_list_Names[sock.fileno()]}: {msgValue}")
            data = f"FRAME_LINE:{player_list_Names[sock.fileno()]}:{msgValue}"
            data = data.encode()

        if msgType == "SERIALIZE":
            print(
                f"Serialize Request from player {player_list_Names[sock.fileno()]}")
            data = f"SERIALIZE:{player_list_Names[sock.fileno()]}:{msgValue}"
            data = data.encode()

    elif len(msgParts) == 1:
        # The lack the split divider "//" indicates this is a word guess.
        msgType = "MESSAGE"
        msgValue = data.decode()
        print(
            f"Msg recognized as word guess from player {player_list_Names[sock.fileno()]}")
        if wordIsCorrect(msgValue):
            data = (
                f"ANSWER:{[player_list_Names[sock.fileno()], str(sock.fileno())]}:{msgValue}").encode()

            print(player_list_Names[sock.fileno()] + " guessed right!")
        else:
            data = (
                f"MESSAGE:{player_list_Names[sock.fileno()]}:{msgValue}").encode()
            print(player_list_Names[sock.fileno()] + " guessed wrong.")
    else:
        print("Msg was not recognized.")
    return data


def broadcast(sock, msg):
    for s in connections:
        if s != sock and s != serverSock:
            try:
                s.send(msg.encode('utf8'))
            except:
                s.close()
                connections.remove(s)


while True:
    readsock, writesock, errsock = select.select(connections, [], [])
    for sock in readsock:
        if sock == serverSock:
            sockfd, addr = serverSock.accept()
            # print("Sockfd",sockfd)
            connections.append(sockfd)
            print(" {} connected".format(addr))
        else:
            try:
                data = sock.recv(buffer)
                if data:
                    info = msgInterpreter(data, sock)
                    sock.send(info)
                    broadcast(sock, info.decode())
            except:
                left_game = f"The player :{player_list_Names[sock.fileno()]}: has left the game."
                print(left_game)
                player_list_Names.pop(sock.fileno(), None)
                # broadcast(sock, left_game.encode())
                sock.close()
                connections.remove(sock)
                continue
serverSock.close()
