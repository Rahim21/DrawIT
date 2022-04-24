from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import json

from tkinter import *
from tkinter import ttk, colorchooser

# CHEMIN ————————————————————
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# FENETRE ————————————————————
window = Tk()

window.geometry("800x600")
window.configure(bg = "#017aa0")

canvas = Canvas(window,bg = "#017aa0",height = 600,width = 800,bd = 0,highlightthickness = 0,relief = "ridge")

canvas.place(x = 0, y = 0)
fenetre_app = PhotoImage(file=relative_to_assets("fenetre_app.png"))
image_1 = canvas.create_image(400.0,300.0,image=fenetre_app)

image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(300.0,275.0,image=image_image_2)

zone_message = PhotoImage(file=relative_to_assets("message.png"))
zone_message_bg = canvas.create_image(700.0,575.0,image=zone_message)
zone_message_1 = Entry(bd=0,bg="#FFFFFF",highlightthickness=0)
zone_message_1.place(x=610.0,y=560.0,width=180.0,height=28.0)

# DEBUT ——————————————————————————————————————————————————
# INITIALISATION ————————————————————
init_x, init_y = None, None # Coordonnées du trait dessiné (point de départ)
pen_color = "black" # Couleur du pinceau
pen_color_tmp = pen_color # Dernière couleur du pinceau avant d'utiliser la gomme
pen_width = 5  # Taille 5/100 par défaut
dashboard_color = "white" # Couleur du dashboard


dashboard = Canvas(window,bg = dashboard_color,height = 400,width = 550,bd = 0,highlightthickness = 0,relief = "ridge")
dashboard.place(x = 25, y = 75)

# Methode pour dessiner sur le dashboard avec <B1-Motion>
def draw(event):
    global init_x, init_y
    global selectLine, poubelle_cleaned, gomme
    #if poubelle_cleaned:
     #   selectLine+=1
      #  poubelle_cleaned = False
    if init_x and init_y:
        dashboard.create_line(init_x,init_y,event.x,event.y,width=pen_width,fill=pen_color,capstyle=ROUND,smooth=True,tag=("gomme" if gomme==True else "line"+str(selectLine)))

    init_x = event.x
    init_y = event.y

def reset(event):
    global init_x, init_y, selectLine
    init_x = None
    init_y = None
    selectLine +=1
    # suppression des couleurs des lignes de redo_list
    if len(redo_list) > 0 and len(poubelle_list_item) == 0 :
        for i in range(len(redo_list)):
            del line_color[0]
    redo_list.clear() # si un nouveau trait est dessiné

def clear():
    global selectLine, poubelle_cleaned
    deleted_line = selectLine
    poubelle_list = [] # Liste des lignes supprimées avec la poubelle
    color_list = [] # Liste des couleurs des lignes supprimées avec la poubelle
    for deleted_line in range(deleted_line):
        for item in dashboard.find_withtag("line"+str(deleted_line)):
            poubelle_list.append(dashboard.coords(item))
            color_list.append(dashboard.itemcget(item, "fill"))
        poubelle_list_item.append(poubelle_list.copy())
        line_color.append(color_list[-1])
        # suppression
        poubelle_list.clear()
        color_list.clear()
    
    redo_list.clear() # On ne peux plus rétablir car nous avons effectué l'action de suppression
    dashboard.delete(ALL) # Efface le dashboard
    poubelle_cleaned = True

def change_pen_color(eraser=False, color="multicolor"):  # pinceau/gomme
    global pen_color, pen_color_tmp, gomme
    if eraser:
        gomme = True
        pen_color_tmp = pen_color
        pen_color = dashboard_color
    elif color == "multicolor":
        pen_color=colorchooser.askcolor(color=pen_color)[1]
        gomme = False
    else:
        pen_color = color
        gomme = False

def change_dashboard_color():  # Change la couleur du dashboard
    global dashboard_color    
    dashboard_color = colorchooser.askcolor(color=dashboard_color)[1]
    dashboard.configure(bg = dashboard_color)
    for item in dashboard.find_withtag("gomme"):
        dashboard.itemconfig(item, fill=dashboard_color)

def change_brush_width(event):  # Change la taille du pinceau à l'aide d'un slider
    global pen_width
    pen_width = event

def undo():
    global selectLine
    if len(poubelle_list_item) > 0:
        item_selected = 0
        for item in poubelle_list_item: # récupérer toute les lignes avec le même tag en 1 item
            for coords in item:
                dashboard.create_line(coords,width=pen_width,fill=line_color[0],capstyle=ROUND,smooth=True, tag="line"+str(item_selected))
            item_selected += 1
            # supprimer la première case de line_color
            del line_color[0]
        #selectLine -= 1
        poubelle_list_item.clear()
    elif selectLine > 0:
        coords_list = [] # Coordonnées des lignes supprimées avec le même tag
        color_list = [] # Couleur des lignes supprimées avec la même couleur
        for item in dashboard.find_withtag("line"+str(selectLine-1)): # récupérer toute les lignes avec le même tag en 1 item
            if dashboard.find_withtag("line"+str(selectLine-1)): # si c'est bien la dernière ligne
                coords_list.append(dashboard.coords(item))
                color_list.append(dashboard.itemcget(item, "fill"))
        redo_list.append(coords_list.copy()) # on fait une copie des coordonnées de l'item
        line_color.append(color_list[0]) # on récupère la couleur de la ligne

        coords_list.clear() # on peux donc supprimer ceci car on a fait au préalable une copie
        color_list.clear()
        dashboard.delete("line"+str(selectLine-1))
        selectLine -= 1
    else:
        print("Aucune ligne à supprimer")

def redo():
    global selectLine
    if len(redo_list) > 0:
        item = redo_list[-1] # on récupère le dernier item
        for coords in item: # on récupère les coordonnées de cette item
            dashboard.create_line(coords,width=pen_width,fill=line_color[-1],capstyle=ROUND,smooth=True, tag="line"+str(selectLine))
        selectLine += 1
        redo_list.pop()
        line_color.pop()
    else:
        print("Aucune ligne à rétablir")


def debug():
    print("———————————————————— Debug : ————————————————————")
    print("line ID : "+str(selectLine))
    print(f"Debug line_color [{len(line_color)}]: ")
    print(line_color)
    print(f"Debug redo_list [{len(redo_list)}] : ")
    print(redo_list)

redo_list = [] # Liste des lignes supprimées
poubelle_list_item = [] # Liste des items supprimés avec la poubelle (par item)
line_color = [] # Couleur du pinceau pour chaque dessin effectué
selectLine = 0
poubelle_cleaned = False
gomme = False
# Dessine un trait du pinceau jusqu'au relachement du clic de la souris
dashboard.bind("<B1-Motion>", draw)
dashboard.bind('<ButtonRelease-1>', reset)




# Création des boutons ——————————————————————————————————————————————————
bouton_dict = {}
liste_bouton = []

CUR_DIR = Path(__file__).parent
fichier_bouton_json = CUR_DIR / "bouton.json"
# si le fichier existe
if fichier_bouton_json.exists():
    with open(fichier_bouton_json, "r") as fichier:
        bouton_dict = json.load(fichier)
else :
    print("Fichier 'bouton.json' introuvable.")
    quit()

def init_Bouton(bouton):
    bouton_img.append(PhotoImage(file=relative_to_assets("bouton/"+bouton+".png")))
    liste_bouton.append(Button(
        image = bouton_img[-1],
        borderwidth=0,
        highlightthickness=0,
        command= eval(bouton_dict[bouton].get("assign", "lambda: print('bouton inconnue')")),
        relief="flat"
    ))
    liste_bouton[-1].place(
        x = bouton_dict[bouton]["x"],
        y = bouton_dict[bouton]["y"],
        width = bouton_dict[bouton]["width"],
        height = bouton_dict[bouton]["height"]
    )

bouton_img = []
for bouton in bouton_dict:
    init_Bouton(bouton)

# Slider pour la taille de la brosse
slider_width = ttk.Scale(from_= 1, to = 100,command=change_brush_width,orient=HORIZONTAL)
slider_width.set(pen_width)
slider_width.grid(row=0,column=1,ipadx=30)
slider_width.place(x=300,y=510)

window.resizable(False, False)
window.mainloop()
