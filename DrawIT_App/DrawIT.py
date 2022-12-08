from Model import Model
from View import View
from Controller import Controller
import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path

class DrawIT(tk.Tk):
    def __init__(self):

        username = input("Please enter your username: ")

        super().__init__()
        self.cleanTerminal()
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.title(f'DrawIT | {username}')
        self.geometry(f"{(self.WIDTH)}x{self.HEIGHT}")
        self.configure(bg="#017aa0")
        icon_path = Path(__file__).parent / Path("assets/drawIT_logo.ico")
        self.iconbitmap(icon_path)
        self.resizable(False, False)

        # create a model
        self.model = Model()
        self.model.player.username = username

        # create a view and place it on the root window
        self.view = View(self)

        # create a controller
        self.controller = Controller(self.model, self.view)

        # set the controller to view
        self.view.set_controller(self.controller)

    def cleanTerminal(self):  # Clears the screen on Linux, Mac & Win.
        if (os.name == "posix"):
            os.system("clear")
        # elif (platform.system() == "Windows"):
        else:
            os.system("cls")

    def close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.controller.close_window()


if __name__ == '__main__':
    game = DrawIT()
    game.protocol("WM_DELETE_WINDOW", game.close_window)
    game.mainloop()
