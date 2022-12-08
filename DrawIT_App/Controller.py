from tkinter import *
from tkinter import colorchooser

import socket
from threading import Thread
import random
import ast
import pickle
import time


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self._obj = None
        self.lastx, self.lasty = None, None
        self.coords = []
        self.tick = False

        self.view.board.bind('<Button-1>', self.click)
        self.view.board.bind("<B1-Motion>", self.draw)
        self.view.board.bind('<ButtonRelease-1>', self.reset)
        self.view.chat.bind("<Return>", self.pressedEnter)

        # SOCKET STUFF:
        self.servIP = "127.0.0.1"
        print(f"servIP from startScr: {self.servIP}\n")
        self.servPort = int(5555)
        print(f"servPort from startScr: {self.servPort}\n")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Socket created: {self.sock}\n")
        except:
            print("Failed to create socket...\n")
        try:
            self.sock.connect((self.servIP, self.servPort))
            print(f"Connected to {self.servIP} on port {self.servPort}!\n")
            self.tick = True
            try:
                self.sendMsg = f"NEW_PLAYER//{self.model.player.username}"
                self.sendMsgNow()
            except:
                print(f"Failed to send {self.model.player.username}...\n")
        except:
            print("Connection to server failed...\n")
            self.view.parent.after(1000, self.close_window)

        # Start receiving data from server:
        self.receivethread = Thread(target=self.receive)
        self.receivethread.start()

    def create_shape(self, shape, the_list, indice=-1):
        if shape in ["line", "straight_line"]:
            return self.view.board.create_line(the_list[indice].coords,
                                               width=the_list[indice].width,
                                               fill=the_list[indice].fill,
                                               capstyle=ROUND,
                                               smooth=True,
                                               tag=the_list[indice].tag)
        elif shape in ["rectangle", "filled_rectangle"]:
            return self.view.board.create_rectangle(the_list[indice].coords,
                                                    width=the_list[indice].width,
                                                    fill=the_list[indice].fill,
                                                    outline=the_list[indice].outline,
                                                    tag=the_list[indice].tag)
        elif shape in ["circle", "filled_circle"]:
            return self.view.board.create_oval(the_list[indice].coords,
                                               width=the_list[indice].width,
                                               fill=the_list[indice].fill,
                                               outline=the_list[indice].outline,
                                               tag=the_list[indice].tag)

    def click(self, event):  # add tag and other for each...
        if self.model.player.the_drawer:
            if not self.model.paint.selected_tool == "line":
                x, y = event.x, event.y

                self.model.board.line_list.append(self.model.Line(type=self.model.paint.selected_tool, coords=[x, y, x, y], width=self.model.paint.pen_width,
                                                                  color=self.model.paint.pen_color, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"]))
                self._obj = self.create_shape(
                    shape=self.model.paint.selected_tool, the_list=self.model.board.line_list)
                self.lastx, self.lasty = x, y
        else:
            pass

    def draw(self, event):
        if self.model.player.the_drawer:
            if self.model.paint.selected_tool == "line":
                if self.model.paint.init_x and self.model.paint.init_y:
                    self.view.board.create_line(self.model.paint.init_x, self.model.paint.init_y, event.x, event.y, width=self.model.paint.pen_width, fill=self.model.paint.pen_color,
                                                capstyle=ROUND, smooth=True, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"])

                    self.sendMsgValue = [self.model.paint.selected_tool, self.model.paint.init_x, self.model.paint.init_y, event.x, event.y, self.model.paint.pen_width, self.model.paint.pen_color,
                                         "line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"]]
                    self.sendMsg = ("FRAME_LINE//"+str(self.sendMsgValue))
                    self.sendMsgNow()

                    self.coords.append([self.model.paint.init_x,
                                        self.model.paint.init_y, event.x, event.y])
                self.model.paint.init_x, self.model.paint.init_y = event.x, event.y
            else:
                x, y = self.lastx, self.lasty
                self.view.board.coords(self._obj, (x, y, event.x, event.y))
                self.model.board.line_list[-1].coords = [x,
                                                         y, event.x, event.y]
        else:
            pass

    def reset(self, event):
        if self.model.player.the_drawer:
            if self.model.paint.selected_tool == "line":
                self.model.board.line_list.append(self.model.Line(type='line', coords=self.coords.copy(), color=self.model.paint.pen_color,
                                                                  width=self.model.paint.pen_width, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"]))
            # self.sendMsgValue = [self.model.paint.selected_tool, self.model.board.line_list[-1].coords, self.model.paint.pen_width, self.model.paint.pen_color,
            #                      "line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"]]
            # self.sendMsg = ("CO//"+str(self.sendMsgValue))
            # self.sendMsgNow()

            self.coords.clear()
            self.model.paint.init_x = None
            self.model.paint.init_y = None
            self.model.board.selectLine += 1
            self.model.board.redo_list.clear()

            # sérialisation de l'objet board
            self.serializeBoard()
        else:
            pass

    def clear(self):
        if self.model.player.the_drawer or self.model.player.compliquer_tache > 0:
            self.model.board.clear_list = self.model.board.line_list.copy()
            self.model.board.line_list.clear()
            self.view.board.delete(ALL)
            self.model.board.redo_list.clear()
            self.change_board_color(reset=True)
            self.serializeBoard("REFRESH")

            self.model.player.compliquer_tache -= 1
        else:
            pass

    def change_pen_color(self, eraser=False, color="multicolor"):
        if eraser:
            self.model.paint.eraser = True
            self.model.paint.selected_tool = "line"
            self.update_selected_tool()
            self.model.paint.pen_color_tmp = self.model.paint.pen_color
            self.model.paint.pen_color = self.model.board.board_color
            self.view.mode_text.set("Mode: eraser")
        elif color == "multicolor":
            self.model.paint.pen_color = colorchooser.askcolor(
                color=self.model.paint.pen_color)[1]
            self.model.paint.eraser = False
            self.view.mode_text.set("Mode: pen")
        else:
            self.model.paint.pen_color = color
            self.model.paint.eraser = False
            self.view.mode_text.set("Mode: pen")
        self.view.custom.configure(background=self.model.paint.pen_color)
        self.view.custom._color = self.model.paint.pen_color

    # pas tout à fait fonctionnel mais tant pis
    def change_board_color(self, reset=False):
        if self.model.player.the_drawer:
            if reset:
                self.model.board.board_color = "white"
            else:
                self.model.board.board_color = colorchooser.askcolor(
                    color=self.model.board.board_color)[1]

            self.view.board.configure(bg=self.model.board.board_color)
            for item_list in self.model.board.line_list:
                if "gomme" in item_list.tag:
                    if item_list.fill != "":
                        self.model.board.line_list[self.model.board.line_list.index(
                            item_list)].fill = self.model.board.board_color
                        self.model.board.line_list[self.model.board.line_list.index(
                            item_list)].outline = self.model.board.board_color
                    else:
                        self.model.board.line_list[self.model.board.line_list.index(
                            item_list)].outline = self.model.board.board_color
            for item_board in self.view.board.find_withtag("gomme"):

                if self.view.board.itemcget(item_board, "fill") != "":
                    # line, straight_line
                    if self.view.board.type(item_board) == "line":
                        self.view.board.itemconfig(
                            item_board, fill=self.model.board.board_color)
                    # filled_rectangle, filled_cercle
                    else:
                        self.view.board.itemconfig(
                            item_board, outline=self.model.board.board_color, fill=self.model.board.board_color)
                # rectangle, cercle
                else:
                    self.view.board.itemconfig(
                        item_board, outline=self.model.board.board_color)
            self.serializeBoard()
        else:
            pass

    def change_brush_width(self, event):
        self.model.paint.pen_width = event

    def pen_width(self):
        return self.model.paint.pen_width

    def current_color(self):
        return self.model.paint.current_color

    def undo(self):
        if self.model.player.the_drawer or self.model.player.compliquer_tache > 0:
            if len(self.model.board.line_list) > 0:
                self.model.board.redo_list.append(
                    self.model.board.line_list[-1])
                if len(self.model.board.line_list[-1].tag) > 1:
                    self.view.board.delete(
                        self.model.board.line_list[-1].tag[0])
                self.view.board.delete(self.model.board.line_list[-1].tag)
                self.model.board.line_list.pop()
                self.model.board.selectLine -= 1
                self.serializeBoard("REFRESH")
            elif len(self.model.board.clear_list) > 0:
                if len(self.model.board.line_list) > 0:
                    self.model.board.clear_list.append(
                        self.model.board.line_list.copy())
                    self.model.board.line_list.clear()
                # test car if inutile maintenant
                for item in self.model.board.clear_list:
                    self.create_shape(
                        shape=item.type, the_list=self.model.board.clear_list, indice=self.model.board.clear_list.index(item))
                    self.model.board.line_list.append(item)
                self.model.board.clear_list.clear()
                self.serializeBoard("REFRESH")
            else:
                print("Aucune ligne à supprimer")

            self.model.player.compliquer_tache -= 1
        else:
            pass

    def redo(self):
        if self.model.player.the_drawer:
            if len(self.model.board.redo_list) > 0:
                item = self.model.board.redo_list[-1]
                if item.type in ["line", "straight_line"]:
                    self.view.board.create_line(item.coords, width=item.width,
                                                fill=item.fill, capstyle=ROUND, smooth=True, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"])
                elif item.type in ["rectangle", "filled_rectangle"]:
                    self.view.board.create_rectangle(
                        item.coords, width=item.width, fill=item.fill, outline=item.outline, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"])
                elif item.type in ["circle", "filled_circle"]:
                    self.view.board.create_oval(item.coords, width=item.width, fill=item.fill,
                                                outline=item.outline, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"])

                self.model.board.line_list.append(item)
                self.model.board.redo_list.pop()
                self.model.board.selectLine += 1
                self.serializeBoard("REFRESH")
            else:
                print("Aucune ligne à rétablir")
        else:
            pass

    def debug(self):
        line = self.model.board.line_list
        redo = self.model.board.redo_list
        print(f"""———————————————————— Debug : ————————————————————
line on board : {str(self.model.board.selectLine)}
line_list : [{len(line)}] {[(line[i].outline if len(line[i].outline)>0 else  line[i].fill, line[i].type) for i in range(len(line))]}

redo_list color [{len(redo)}] : {[redo[i].outline if len(redo[i].outline)>0 else  redo[i].fill for i in range(len(redo))]}
redo_list last coords : {redo[-1].coords if len(redo)>0 else "None"}
redo_list all coords : {[redo[i].coords for i in range(len(redo))]}
word : {self.model.game.word}
        """)

    def update_selected_tool(self, tool="line"):
        self.model.paint.selected_tool = tool
        self.view.shape_text.set("Shape: "+tool)

    def close_window(self):
        self.tick = False
        self.view.parent.destroy()

    def pressedEnter(self, event):
        self.sendMsg = self.view.chat.get("1.0", END).strip()
        if self.sendMsg:
            print("Message sent !")
            self.sendMsgNow()
        self.view.chat.delete(1.0, END)

    def sendMsgNow(self):
        self.sock.send(str(self.sendMsg).encode('utf8'))

    def receive(self):
        while self.tick:
            try:
                self.msg = self.sock.recv(1024)
                self.msgParts = self.msg.decode('utf8').split(":")
                print(f"msgPart {self.msgParts}")
                if len(self.msgParts) == 3:
                    self.msgType = self.msgParts[0]
                    self.msgName = self.msgParts[1]
                    self.msgValue = self.msgParts[2]
                    self.msgRouter()
                else:
                    continue
            except:
                print("Receive error")

    # Trie des informations qui transitent
    def msgRouter(self):
        if self.msgType == "FRAME_LINE":
            # msgValue: Paint Coordinates
            self.recreatePaint()
        if self.msgType == "SERIALIZE":
            # msgValue: Paint Coordinates
            self.rePaint(self.msgValue)

        self.view.textbox.config(state=NORMAL)  # enable textbox to write

        if self.msgType == "MESSAGE":
            # msgValue: Player Message
            self.chat_box = f"{self.msgName}: {self.msgValue}\n"
            self.view.textbox.insert(END, self.chat_box)
            self.view.textbox.see("end")
        elif self.msgType == "ANSWER":
            found = False
            user_data = ast.literal_eval(self.msgName)
            if self.model.game.timer > 0:
                # change self.msgName to list
                found = True
                self.chat_box = f"{user_data[0]} À TROUVÉ !\n"
                print(f"data: {user_data[1]}, id {self.model.player.id}")
                if user_data[1] == self.model.player.id and not self.model.player.has_the_answer:
                    if not self.model.player.the_drawer:
                        self.model.player.score += self.model.game.timer

                        timer_score = self.model.game.timer//4
                        score_data = [self.model.player.score, str(timer_score)]
                        self.sendMsg = f"SCORE//{score_data}"
                        self.sendMsgNow()
                    else:
                        score_data = [self.model.player.score, str(0)]
                        self.sendMsg = f"SCORE//{score_data}"
                        self.sendMsgNow()

                    self.model.player.has_the_answer = True
                print(f"{user_data[0]} score : {self.model.player.score}")
            else:
                self.chat_box = f"Trop tard {user_data[0]} ...\n"
            # debug : configure textbox fg for green
            self.view.textbox.tag_config(
                'guessed', foreground="green", font=("Helvetica", 12, "bold"))
            if found:
                self.view.textbox.insert(END, self.chat_box, "guessed")
            else:
                self.view.textbox.insert(END, self.chat_box)

        if self.msgType == "//":
            # msgValue: Chat Comment
            self.chat_box = f"// {self.msgName}: {self.msgValue}\n"
            self.view.textbox.insert(END, self.chat_box)
            self.view.textbox.see("end")

        if self.msgType == "PLAYER_ID":
            # msgValue: set the player id
            if self.model.player.id == None:
                self.model.player.id = self.msgValue

        if self.msgType == "START_GAME":
            # msgValue: the new hidden word
            self.model.player.score = 0
            self.model.game.leaderboard = pickle.load(
                open("leaderboard_data.p", "rb"))
            self.initRound()

        if self.msgType == "SCORE":
            # msgValue: the new score
            self.model.game.leaderboard = pickle.load(
                open("leaderboard_data.p", "rb"))
            print(
                f"Leaderboard : {self.model.game.leaderboard}")

            # convert SCORE str to int
            for key, value in self.model.game.leaderboard.items():
                value['SCORE'] = int(value['SCORE'])

            # sort the dict of dict by SCORE descending
            leaderboard = sorted(
                self.model.game.leaderboard.items(), key=lambda k_v: k_v[1]['SCORE'], reverse=True)

            # convert list to dict
            leaderboard = dict(leaderboard)

            self.view.leaderboard_text.config(
                state=NORMAL)  # enable leaderboard text
            self.view.leaderboard_text.delete(1.0, END)
            lb_data = f'        LEADERBOARD\n\n\n'
            self.view.leaderboard_text.insert(END, lb_data, ("bold", "20"))

            # display leaderboard format [rank] : [user] - [score] point(s)
            for i, (key, value) in enumerate(leaderboard.items()):
                lb_data = f' [{i+1}] {value["USERNAME"]} - {value["SCORE"]} 🟢\n'
                self.view.leaderboard_text.insert(END, lb_data, ("bold", "10"))

            self.view.leaderboard_text.config(
                state=DISABLED)  # disable leaderboard textbox

        if self.msgType == "NEW_WORD":
            # désactiver le canvas et palette à outils pour les non dessinateur ! + clear canvas

            # patienter 2 secondes avant de lancer le prochain tour
            self.resetCanvas()
            self.view.timer_label.after(2000)  # ou un time.sleep(2)
            self.initRound()

        if self.msgType == "END_GAME":
            # Display end of GAME on textbox
            self.view.textbox.config(state=NORMAL)  # enable textbox to write
            # red END game text
            self.view.textbox.insert(
                END, "\n----- END OF GAME -----\n", ("bold", "20"))
            self.view.textbox.config(state=DISABLED)  # disable textbox
            self.model.player.the_drawer = False

        if self.msgType == "CHEAT":
            # msgValue: Cheat!
            if self.msgName == self.model.player.id:  # self.playerName
                self.sendMsg = f"NEW_PLAYER//{self.model.player.username}(cheater)"
                self.sendMsgNow()
                self.inTheBox = self.msgValue
                self.view.chat.insert(END, self.inTheBox)
                self.view.chat.see("end")

        # disable textbox after each message
        self.view.textbox.config(state=DISABLED)

    def initRound(self):
        round_data = ast.literal_eval(self.msgValue)

        self.model.player.has_the_answer = False
        self.model.game.word = round_data[0]  # the word

        if self.model.player.id == round_data[1]:
            self.view.hidden_word.set(self.model.game.word)
            print(f"{self.model.player.username} is the drawer")
            self.model.player.the_drawer = True
        else:
            self.view.hidden_word.set(
                f"{self.model.game.word[0]} {'_ ' * (len(self.model.game.word)-1)}")
            print(f"{self.model.player.username} is not the drawer")
            self.model.player.the_drawer = False
        # set to 80 after debugging, get these data from the server [round, time for draw]
        # self.view.board.config(state=NORMAL)
        if self.model.game.duration == None:
            self.model.game.duration = round_data[2]
        self.view.board.delete("all")
        self.view.timer_label.after(
            1000, self.countdown, self.model.game.duration)

    def countdown(self, t):
        self.model.game.timer = t
        if t >= 0:
            if t < 10:
                self.view.timer_label.config(bg="red")
            elif t < 50:
                self.view.timer_label.config(bg="orange")
            else:
                self.view.timer_label.config(bg="#9ff5ac")
            self.view.timer.set(f"{t} sec.")
            t -= 1
            self.view.timer_label.after(1000, self.countdown, t)
        else:
            print("Turn Ended")
            self.showAnswer()

    def serializeBoard(self, option=""):
        pickle.dump(self.model.board, open("board_data.p", "wb"))
        the_data = f"SERIALIZE//{option}"
        self.sock.send(str(the_data).encode('utf8'))
        print("Send the canvas to the server...\n")

    def rePaint(self, option):
        # self.view.board = ast.literal_eval(self.msgValue) # envoie sans fichier
        self.model.board = pickle.load(open("board_data.p", "rb"))

        # clear only for undo, redo, other...
        self.view.board.configure(bg=self.model.board.board_color)
        if option == "REFRESH":
            self.view.board.delete("all")
            for item in self.model.board.line_list:
                self.create_shape(
                    shape=item.type, the_list=self.model.board.line_list, indice=self.model.board.line_list.index(item))
        else:
            item = self.model.board.line_list[-1]
            self.create_shape(
                shape=item.type, the_list=self.model.board.line_list, indice=self.model.board.line_list.index(item))

        # update the canvas for the changes to be visible : but need to serialise self.view.board (_tkinter.tkapp' object)
        self.view.board.update_idletasks()
        self.view.board.update()
        print("repainted !!!!!!!!!!")

    def recreatePaint(self):
        self.repaint = ast.literal_eval(self.msgValue)
        if self.repaint[0] == "line":
            self.view.board.create_line(self.repaint[1], self.repaint[2], self.repaint[3], self.repaint[4],
                                        width=self.repaint[5], fill=self.repaint[6], capstyle=ROUND, smooth=True, tag=self.repaint[7])

    def showAnswer(self):
        self.view.hidden_word.set(self.model.game.word)
        # generate a new word

        # debug : envoyé par le dessinateur (1 seul client !!!)
        if self.model.player.the_drawer:
            print(
                f"pseudooooooooooo : {self.model.player.username}, drawer : {self.model.player.the_drawer}")
            #self.sendMsg = f"NEW_WORD//{self.model.game.word}"
            self.sendMsg = f"//NEW_WORD"
            self.sendMsgNow()

    def resetCanvas(self):
        self.model.board.line_list.clear()
        self.model.board.redo_list.clear()
        self.model.board.clear_list.clear()
        self.model.board.board_color = 'white'
        self.model.board.selectLine = 0

        self.view.board.configure(bg=self.model.board.board_color)

        # call reset if mouse is not released
        # self.view.board.bind("<Button-1>", self.reset)
        # self.view.board.config(state=DISABLED)
        self.view.board.delete("all")
