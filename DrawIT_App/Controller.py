from tkinter import *
from tkinter import colorchooser


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self._obj = None
        self.lastx, self.lasty = None, None

        self.coords = []

        self.view.board.bind('<Button-1>', self.click)
        self.view.board.bind("<B1-Motion>", self.draw)
        self.view.board.bind('<ButtonRelease-1>', self.reset)

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
        if not self.model.paint.selected_tool == "line":
            x, y = event.x, event.y

            self.model.board.line_list.append(self.model.Line(type=self.model.paint.selected_tool, coords=[x, y, x, y], width=self.model.paint.pen_width,
                                                              color=self.model.paint.pen_color, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"]))
            self._obj = self.create_shape(
                shape=self.model.paint.selected_tool, the_list=self.model.board.line_list)
            self.lastx, self.lasty = x, y

    def draw(self, event):
        if self.model.paint.selected_tool == "line":
            if self.model.paint.init_x and self.model.paint.init_y:
                self.view.board.create_line(self.model.paint.init_x, self.model.paint.init_y, event.x, event.y, width=self.model.paint.pen_width, fill=self.model.paint.pen_color,
                                            capstyle=ROUND, smooth=True, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"])
                self.coords.append([self.model.paint.init_x,
                                    self.model.paint.init_y, event.x, event.y])
            self.model.paint.init_x, self.model.paint.init_y = event.x, event.y
        else:
            x, y = self.lastx, self.lasty
            self.view.board.coords(self._obj, (x, y, event.x, event.y))
            self.model.board.line_list[-1].coords = [x, y, event.x, event.y]

    def reset(self, event):
        if self.model.paint.selected_tool == "line":
            self.model.board.line_list.append(self.model.Line(type='line', coords=self.coords.copy(), color=self.model.paint.pen_color,
                                                              width=self.model.paint.pen_width, tag="line"+str(self.model.board.selectLine) if not self.model.paint.eraser else ["line"+str(self.model.board.selectLine), "gomme"]))
        self.coords.clear()
        self.model.paint.init_x = None
        self.model.paint.init_y = None
        self.model.board.selectLine += 1
        if len(self.model.board.redo_list) > 0 and len(self.model.board.poubelle_list_item) == 0:
            self.model.board.line_color.clear()
        self.model.board.redo_list.clear()

    def clear(self):
        self.model.board.clear_list = self.model.board.line_list.copy()
        self.model.board.line_list.clear()
        self.view.board.delete(ALL)
        self.model.board.redo_list.clear()
        self.change_board_color(reset=True)

    def change_pen_color(self, eraser=False, color="multicolor"):
        if eraser:
            self.model.paint.eraser = True
            self.model.paint.pen_color_tmp = self.model.paint.pen_color
            self.model.paint.pen_color = self.model.paint.board_color
        elif color == "multicolor":
            self.model.paint.pen_color = colorchooser.askcolor(
                color=self.model.paint.pen_color)[1]
            self.model.paint.eraser = False
        else:
            self.model.paint.pen_color = color
            self.model.paint.eraser = False

    # pas tout à fait fonctionnel mais tant pis
    def change_board_color(self, reset=False):
        if reset:
            self.model.paint.board_color = "white"
        else:
            self.model.paint.board_color = colorchooser.askcolor(
                color=self.model.paint.board_color)[1]

        self.view.board.configure(bg=self.model.paint.board_color)
        for item_list in self.model.board.line_list:
            if "gomme" in item_list.tag:
                if item_list.fill != "":
                    self.model.board.line_list[self.model.board.line_list.index(
                        item_list)].fill = self.model.paint.board_color
                    self.model.board.line_list[self.model.board.line_list.index(
                        item_list)].outline = self.model.paint.board_color
                else:
                    self.model.board.line_list[self.model.board.line_list.index(
                        item_list)].outline = self.model.paint.board_color
        for item_board in self.view.board.find_withtag("gomme"):

            # print the type of the item of the board if is a line or rectangle
            if self.view.board.type(item_board) == "line":
                print("line")
            elif self.view.board.type(item_board) == "rectangle":
                print("rectangle")
            elif self.view.board.type(item_board) == "oval":
                print("cercle")

            if self.view.board.itemcget(item_board, "fill") != "":
                # line, straight_line
                if self.view.board.type(item_board) == "line":
                    self.view.board.itemconfig(
                        item_board, fill=self.model.paint.board_color)
                # filled_rectangle, filled_cercle
                else:
                    self.view.board.itemconfig(
                        item_board, outline=self.model.paint.board_color, fill=self.model.paint.board_color)
            # rectangle, cercle
            else:
                self.view.board.itemconfig(
                    item_board, outline=self.model.paint.board_color)

    def change_brush_width(self, event):
        self.model.paint.pen_width = event

    def pen_width(self):
        return self.model.paint.pen_width

    def undo(self):
        if len(self.model.board.line_list) > 0:
            self.model.board.redo_list.append(self.model.board.line_list[-1])
            if len(self.model.board.line_list[-1].tag) > 1:
                self.view.board.delete(self.model.board.line_list[-1].tag[0])
            self.view.board.delete(self.model.board.line_list[-1].tag)
            self.model.board.line_list.pop()
            self.model.board.selectLine -= 1
        elif len(self.model.board.clear_list) > 0:
            if len(self.model.board.line_list) > 0:
                self.model.board.clear_list.append(
                    self.model.board.line_list.copy())
                self.model.board.line_list.clear()
            for item in self.model.board.clear_list:
                self.create_shape(
                    shape=item.type, the_list=self.model.board.clear_list, indice=self.model.board.clear_list.index(item))
                self.model.board.line_list.append(item)
            self.model.board.clear_list.clear()
        else:
            print("Aucune ligne à supprimer")

    def redo(self):
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
        else:
            print("Aucune ligne à rétablir")

    def debug(self):
        line = self.model.board.line_list
        redo = self.model.board.redo_list
        print(f"""———————————————————— Debug : ————————————————————
line on board : {str(self.model.board.selectLine)}
line_list : [{len(line)}] {[(line[i].outline if len(line[i].outline)>0 else  line[i].fill, line[i].type) for i in range(len(line))]}

redo_list color [{len(redo)}] : {[redo[i].outline if len(redo[i].outline)>0 else  redo[i].fill for i in range(len(redo))]}
redo_list last coords : {redo[-1].coords if len(redo)>0 else "None"}
redo_list all coords : {[redo[i].coords for i in range(len(redo))]}
        """)

    def update_selected_tool(self, tool="line"):
        self.model.paint.selected_tool = tool
