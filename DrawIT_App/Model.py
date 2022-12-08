class Model:
    def __init__(self):
        self.paint = Paint()
        self.board = Board()
        self.player = Player()

    class Line:
        def __init__(self, type='line', coords=None, color='', width=5, tag='line'):
            self.type = type
            self.coords: list = []
            self.coords.append(coords)
            self.width = width
            self.tag = tag
            self.fill = ''
            self.outline = ''

            if type not in ['rectangle', 'circle']:
                self.fill = color
            if type not in ['line', 'straight_line']:
                self.outline = color


class Paint:
    def __init__(self):
        self.init_x, self.init_y = None, None
        self.pen_color = 'black'
        self.pen_color_tmp = self.pen_color
        self.pen_width = 5
        self.board_color = 'white'
        self.eraser = False
        self.selected_tool = 'line'


class Board:
    def __init__(self):
        self.line_list: list[Model.Line] = []
        self.line_coords_list = []
        self.redo_list: list[Model.Line] = []
        self.clear_list: list[Model.Line] = []

        #self.redo_list = []
        self.line_color = []
        self.poubelle_list_item = []
        self.selectLine = 0


class Player:
    def __init__(self, username="Player", score=0, the_drawer=False):
        self.username = username
        self.score = score
        self.the_drawer = the_drawer


class Chat:
    def __init__(self):
        self.messages = []
