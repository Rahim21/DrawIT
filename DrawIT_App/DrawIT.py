from Model import Model
from View import View
from Controller import Controller
import tkinter as tk


class DrawIT(tk.Tk):
    def __init__(self):
        super().__init__()
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.title('DrawIT | MVC')
        self.geometry(f"{(self.WIDTH)}x{self.HEIGHT}")
        self.configure(bg="#017aa0")
        self.resizable(False, False)

        # create a model
        model = Model()

        # create a view and place it on the root window
        view = View(self)

        # create a controller
        controller = Controller(model, view)

        # set the controller to view
        view.set_controller(controller)


if __name__ == '__main__':
    game = DrawIT()
    game.mainloop()
