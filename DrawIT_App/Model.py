class Model:
    def __init__(self):
        self.paint = Paint()
        self.board = Board()
        self.player = Player()
        self.game = Game()

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
        self.current_color = None
        self.init_x, self.init_y = None, None
        self.pen_color = 'black'
        self.pen_color_tmp = self.pen_color
        self.pen_width = 5
        self.eraser = False
        self.selected_tool = 'line'


class Board:
    def __init__(self):
        self.line_list: list[Model.Line] = []
        self.redo_list: list[Model.Line] = []
        self.clear_list: list[Model.Line] = []
        self.board_color = 'white'
        self.selectLine = 0


class Player:
    def __init__(self, username="Player", the_drawer=False):
        self.id = None
        self.username = username
        self.score = 0
        self.has_the_answer = False
        # s'il est False alors on affiche pas la barre d'outil dans la vue
        self.the_drawer = the_drawer
        self.compliquer_tache = 2


class Game:
    def __init__(self):
        self.word = None
        self.duration = None
        self.timer = None
        self.leaderboard = None
