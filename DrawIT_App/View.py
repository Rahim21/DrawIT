import tkinter as tk
from tkinter import ttk

from tkinter import *
from pathlib import Path
import json


# ———————————————————— PATH ————————————————————
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


class View(ttk.Frame):
    """The View class is the view of the MVC.

    Args:
        ttk (View): The view presents the model information to the user. 
    """

    def __init__(self, parent):
        """Initialize the view

        Args:
            parent (tk.Tk): the parent window
        """
        super().__init__(parent)

        self.parent = parent

        # Set the controller
        self.controller = None

        # Create Canvas
        self.canvas = tk.Canvas(parent, bg="red", height=700,
                                width=1000, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)

        # Add image to the canvas
        self.fenetre_app = PhotoImage(
            file=self.relative_to_assets("fenetre_app.png"))
        self.canvas.create_image(
            parent.WIDTH/2, parent.HEIGHT/2, image=self.fenetre_app)

        # Create the board
        self.board_color = "white"
        self.board = Canvas(parent, bg=self.board_color, height=500,
                            width=675, bd=0, highlightthickness=0, relief="ridge")
        self.board.place(x=25, y=75)

        # create leaderboard
        self.leaderboard_text = Text(parent, bg="#b2e3f7", height=22,
                                     width=25, bd=0, highlightthickness=0, borderwidth=1)
        self.leaderboard_text.place(x=810, y=70)
        self.leaderboard_text.config(state=DISABLED)

        # Create the chat
        self.textbox = Text(parent, bg="white", height=20,
                            width=25, bd=0, highlightthickness=0, borderwidth=1)
        self.textbox.place(x=810, y=385)

        self.chat = Text(parent, bg="white", height=2,
                         width=25, bd=0, highlightthickness=0, borderwidth=1, relief="sunken")
        self.chat.place(x=810, y=660)
        # désactiver le curseur Textbox

        # Create info bar
        self.mode_text, self.shape_text, self.compliquer_text = tk.StringVar(
        ), tk.StringVar(), tk.StringVar()

        self.mode_text.set("Mode: pen")
        self.mode = Label(parent, bg="#017aa0",
                          textvariable=self.mode_text, font=("Helvetica", 12))
        self.mode.place(x=560, y=610)

        self.shape_text.set("Shape: line")
        self.shape = Label(parent, bg="#017aa0",
                           textvariable=self.shape_text, font=("Helvetica", 12))
        self.shape.place(x=560, y=630)

        self.current_color = Label(
            parent, bg="#017aa0", text="Color: ", font=("Helvetica", 12))
        self.current_color.place(x=560, y=650)

        self.color_frame = Frame(parent, height=20, width=20)
        self.color_frame.pack_propagate(False)
        self.color_frame.pack(padx=6, pady=3)

        self.custom = Label(
            self.color_frame, relief='raised', background="#000")
        self.custom.pack(fill=BOTH, expand=1)
        self.color_frame.place(x=600, y=650)

        self.compliquer_text.set(
            """Chaque joueur peut compliquer 
            la tâche au dessinateur (2 fois) (undo/clear)
            """)
        self.compliquer = Label(parent, bg="#017aa0",
                                textvariable=self.compliquer_text, font=("Helvetica", 10), fg="white")
        self.compliquer.place(x=520, y=670)

        # Hidden word
        self.hidden_word = tk.StringVar()
        self.hidden_word_label = Label(parent, bg="#FFF",
                                       textvariable=self.hidden_word, font=("Helvetica", 30))
        self.hidden_word_label.place(x=450, y=10)

        # Init button
        self.bouton_dict = {}
        self.liste_bouton = []
        self.bouton_img = []

        CUR_DIR = Path(__file__).parent
        fichier_bouton_json = CUR_DIR / "bouton.json"
        # si le fichier existe
        if fichier_bouton_json.exists():
            with open(fichier_bouton_json, "r") as fichier:
                self.bouton_dict = json.load(fichier)
        else:
            print("Fichier 'bouton.json' introuvable.")
            quit()

        # Slider pour la taille de la brosse
        slider_width = ttk.Scale(
            from_=1, to=100, command=self.save_brush_width, orient=HORIZONTAL, length=130)
        slider_width.set(5)

        slider_width.place(x=260, y=610)

        # Create timer for the game
        self.timer = tk.StringVar()
        self.timer_label = Label(parent, bg="#9ff5ac",
                                 textvariable=self.timer, font=("Helvetica", 20))
        self.timer.set("? sec.")
        self.timer_label.place(x=710, y=500)

    def set_controller(self, controller):
        """Set the controller

        Args:
            controller (Controller): update the controller
        """
        self.controller = controller
        for bouton in self.bouton_dict:
            self.init_Bouton(bouton)

    def save_brush_width(self, event):
        """Update the brush width

        Args:
            event (int): new brush size
        """
        if self.controller:
            self.controller.change_brush_width(event)

    def get_pen_width(self):
        """Get the pen width

        Returns:
            int: return the new width
        """
        if self.controller:
            return self.controller.pen_width()

    def relative_to_assets(self, path: str) -> Path:
        """Path to the asset folder

        Args:
            path (str): file or other path that is in the parent folder asset

        Returns:
            Path: the path to your file or other folder from this parent asset
        """
        return ASSETS_PATH / Path(path)

    def init_Bouton(self, bouton):
        """Initialize the buttons

        Args:
            bouton (str): key button with its values from a dictionary
        """
        self.bouton_img.append(PhotoImage(
            file=self.relative_to_assets('bouton/'+bouton+'.png')))
        self.liste_bouton.append(Button(
            image=self.bouton_img[-1],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: eval(self.bouton_dict[bouton].get(
                'assign', "print('bouton inconnue')")),
            relief='flat'
        ))
        self.liste_bouton[-1].place(
            x=self.bouton_dict[bouton]["x"],
            y=self.bouton_dict[bouton]["y"],
            width=self.bouton_dict[bouton]["width"],
            height=self.bouton_dict[bouton]["height"]
        )


if __name__ == '__main__':
    print(View.__doc__)
    print(View.__init__.__doc__)
    print(View.set_controller.__doc__)
    print(View.save_brush_width.__doc__)
    print(View.get_pen_width.__doc__)
    print(View.relative_to_assets.__doc__)
    print(View.init_Bouton.__doc__)
