import colorama

from random import randint
from time import sleep


class BoardException(Exception):
    pass


class OutOfBoard(BoardException):
    def __str__(self):
        return "Вы вышли за пределы доски"


class OutOfRange(BoardException):
    def __str__(self):
        return "Вы вышли за пределы поля"


class UnexpectedValue(Exception):
    def __str__(self):
        return "Введено недопустимое значение. Следуйте указаниям программы"


class CellIsBusy(BoardException):
    def __str__(self):
        return "Невозможно установить маркер в данную ячейку. Выберите пустую ячейку в рамках игровоой доски"


class Field:
    def __init__(self, hidden=True):
        self.grid = None
        self.field = None
        self.busy = []
        self.shooten = []
        self.ships = []
        self.alive = 0
        self.damaged = 0
        self.destroyed = 0
        self.sucsess = True
        self.hidden = hidden
        self.hitmark = None
        self.looser = False

    def make_field(self):
        self.field = [['~'] * self.grid for i in range(self.grid)]

    def get_field(self):
        return self.field

    def set_mark(self, x, y, point):
        self.field[x][y] = point

    def shot(self, dot):
        target = self.field[dot.x][dot.y]
        self.hitmark = 0
        if target == "■":
            for ship in self.ships:
                if dot in ship.dots:
                    ship.lives -= 1
                    self.hitmark = 1
                    if ship.damaged == False:
                        self.damaged += 1
                        ship.damaged = True
                    if ship.lives <= 0:
                        ship.damaged = False
                        ship.destroyed = True
                        self.damaged -= 1
                        self.destroyed += 1
                        self.alive -= 1
                        self.hitmark = 2
                    break
                else:
                    continue
            self.set_mark(dot.x, dot.y, point="X")
            self.shooten.append(dot)
        elif target == '~':
            self.set_mark(dot.x, dot.y, point="T")
            self.shooten.append(dot)

    @property
    def get_grid(self):
        return self.grid

    @get_grid.setter
    def get_grid(self, grid_value):
        if grid_value not in ["6", "8", "10", "12", 6, 8, 10, 12]:
            raise UnexpectedValue
        else:
            self.grid = int(grid_value)

    def field_update(self, colour):
        # Рисуем оглавление столбцов
        nums = "    |"
        for x in range(1, self.grid + 1):
            if len(str(x)) < 2:
                nums = nums + f" {x} |"
            else:
                nums = nums + f" {x}|"
        # Рисуем поле с оглавлением строк
        counter = 1
        field = ""
        for i in self.field:
            f_string = ""
            for n in i:
                f_string = f_string + " | " + n
            if len(str(counter)) <= 1:
                f_string = str(counter) + "  " + f_string + " |"
            else:
                f_string = str(counter) + " " + f_string + " |"
            if self.hidden:
                f_string = f_string.replace("■", "~")
            field = field + f_string + "\n"
            counter += 1
        return colour + nums + "\n" + field

    def out(self, dot):
        return not((0 <= dot.x < self.grid) and (0 <= dot.y < self.grid))

    def contour(self, ship):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for x, y in near:
                c_dot = Dot((d.x + x), (d.y + y))
                if not self.out(c_dot) and c_dot not in self.busy:
                    self.busy.append(c_dot)

    def add_ship(self, ship):
        self.ships.append(ship)
        for d in ship.dots:
            self.set_mark(d.x, d.y, "■")
            self.busy.append(d)
        self.contour(ship)
        self.alive += 1

    def cleanup(self):
        self.make_field()
        self.busy = []
        self.ships = []
        self.alive = 0
        self.damaged = 0
        self.destroyed = 0
        self.sucsess = True

    def check_loose(self):
        if self.alive <= 0:
            self.looser = True


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, lives):
        self.lives = lives
        self.dots = []
        self.damaged = False
        self.destroyed = False

    def append_dot(self, dot):
        if dot in self.dots:
            raise CellIsBusy
        else:
            self.dots.append(dot)


class Player:
    def __init__(self, name = "Player1"):
        self.__name = name
        self.shot = None

    @property
    def player_name(self):
        return self.__name

    @player_name.setter
    def player_name(self, name):
        self.__name = name

    def aim(self, aim):
        aim = input().split()
        if len(aim) != 2:
            raise UnexpectedValue
        else:
            x, y = aim

        if not (x.isdigit()) or not (y.isdigit()):
            raise UnexpectedValue
        else:
            self.shot = Dot(int(x)-1, int(y)-1)


class EnemyComputer():
    def __init__(self, difficult=1):
        self.__difficult = difficult
        self.names = ["Билли", "Джон", "Фредди", "Карл", "Эд", "Боб", "Гарри", "Тонни", "Никилянджело", "Санчо", "Дэйл"]
        self.rank = ["Злобный", "Немытый", "Грязный", "Скользкий", "Пылающий", "Пьяный", "Ворчун", "Матершинник", "Вонючка", "Криворукий", "Тупой", "Красавчик", "Вероломный"]
        self.name = None
        self.shot = None

    def name_constructor(self):
        self.name = "Капитан" + " " + self.rank[randint(0, len(self.rank) - 1)] + " " + self.names[randint(0, len(self.names) - 1)]

    def player_name(self):
        return self.name

    def aim(self, n):
        self.shot = Dot(randint(0, n), randint(0, n))


class Message:
    def __init__(self):
        colorama.init(autoreset=True)
        self.p1_name = None
        self.p2_name = None
        self.p1_field = None
        self.p2_field = None
        self.grid = None
        self.green = colorama.Fore.GREEN
        self.red = colorama.Fore.RED

    def set_names(self, p1, p2):
        self.p1_name, self.p2_name = p1, p2

    def set_fields(self, p1, p2):
        self.p1_field, self.p2_field = p1, p2

    def set_grid(self, grid):
        self.grid = grid

    @staticmethod
    def greeting():
        return colorama.Fore.BLUE + """        
        ##   ##    ####   ####     ### ##   
        ##   ##     ##     ##       ##  ##  
        ##   ##     ##     ##       ##  ##  
        ## # ##     ##     ##       ##  ##  
        # ### #     ##     ##       ##  ##  
         ## ##      ##     ##  ##   ##  ##  
        ##   ##    ####   ### ###  ### ##   
             ## ##   ### ###    ##     
            ##   ##   ##  ##     ##    
            ####      ##       ## ##   
             #####    ## ##    ##  ##  
                ###   ##       ## ###  
            ##   ##   ##  ##   ##  ##  
             ## ##   ### ###  ###  ## 
 ### ##     ##     #### ##  #### ##  ####     ### ###  
 ##  ##     ##    # ## ##  # ## ##   ##       ##  ##  
 ##  ##   ## ##     ##       ##      ##       ##      
 ## ##    ##  ##    ##       ##      ##       ## ##   
 ##  ##   ## ###    ##       ##      ##       ##      
 ##  ##   ##  ##    ##       ##      ##  ##   ##  ##  
### ##   ###  ##   ####     ####    ### ###  ### ### """ + \
            colorama.Style.RESET_ALL + \
            "\n---------------Нажмите Enter, чтобы начать игру---------------"

    @staticmethod
    def rules():
        return ['~ - море(пустая клетка)', '■ - ячейка корабля', 'X - попадание', 'T - промах']

    @staticmethod
    def choose_mode():
        return """
---------------Выберите режим игры---------------
---------------1. Одиночная игра-----------------
---------------2. Совместная игра----------------"""

    @staticmethod
    def input_name_p1():
        return "---------------Введите ваше имя---------------"

    @staticmethod
    def input_name_p2():
        return """
-----------------Второй игрок-----------------
---------------Введите ваше имя---------------"""

    def vs(self):
        return "\nМорсквая битва:\n \n" + self.green + self.p1_name + \
            colorama.Style.RESET_ALL + "\n-------------------VS---------------------\n" + \
            self.red + self.p2_name

    @staticmethod
    def field_size():
        return "Выберите размер поля: 6, 8, 10, 12"

    @staticmethod
    def again():
        return """
-------------------Играть еще?-------------------
-----------------1. Продолжить-------------------
-------------------2. Выход----------------------"""

    def fields_update(self, second=False):
        if not second:
            return "Поле игрока: " + self.green + self.p1_name + "\n" * 2 + \
                self.p1_field.field_update(self.green) + colorama.Style.RESET_ALL + \
                "\nКораблей: " + str(self.p1_field.alive) + "\nПодбитых: " + str(self.p1_field.damaged) \
                + "\nУничтожено: " + str(self.p1_field.destroyed) + "\n" * 2 + "Поле игрока: " \
                + self.red + self.p2_name + "\n" * 2 + self.p2_field.field_update(self.red) + \
                colorama.Style.RESET_ALL + "\nКораблей: " + str(self.p2_field.alive) + "\nПодбитых: " + \
                str(self.p2_field.damaged) + "\nУничтожено: " + str(self.p2_field.destroyed) + "\n"
        else:
            return "Поле игрока: " + self.red + self.p2_name + "\n" * 2 + \
                self.p2_field.field_update(self.red) + "\n" * 2 + colorama.Style.RESET_ALL + "\nКораблей: " \
                + str(self.p2_field.alive) + "\nПодбитых: " + str(self.p2_field.damaged) \
                + "\nУничтожено: " + str(self.p2_field.destroyed) + "\n" * 2 + "Поле игрока: " \
                + self.green + self.p1_name + "\n" * 2 + self.p1_field.field_update(self.green) + \
                colorama.Style.RESET_ALL + "\nКораблей: " + str(self.p1_field.alive) + "\nПодбитых: " + \
                str(self.p1_field.damaged) + "\nУничтожено: " + str(self.p1_field.destroyed) + "\n"

    def move(self, second=False):
        if not second:
            return self.green + "Ход игрока: " +  self.p1_name \
                + "\n" + "Введите номер строки и номер столбца через пробел:"
        else:
            return self.red + "Ход игрока: " + self.p2_name \
                + "\n" + "Введите номер строки и номер столбца через пробел:"

    @staticmethod
    def row_number():
        return "Ход номер: "

    @staticmethod
    def splitter():
        return "-" * 100

    def hitmark(self, second=False):
        if not second:
            if self.p2_field.hitmark == 0:
                return "Мимо!"
            elif self.p2_field.hitmark == 1:
                return "Подбит один из кораблей " + self.red + self.p2_name
            else:
                return "Уничтожен корабль " + self.red + self.p2_name
        else:
            if self.p1_field.hitmark == 0:
                return "Мимо!"
            elif self.p1_field.hitmark == 1:
                return "Подбит один из кораблей " + self.green + self.p1_name
            else:
                return "Уничтожен корабль " + self.green + self.p1_name

    def winner(self, second=False):
        if not second:
            return self.green + "-" * 10 + "Игра окончена " + "-" * 10 + "\n" + "-" * 10 + "Победил " + self.p1_name + "-" * 10
        else:
            return self.red + "-" * 10 + "Игра окончена " + "-" * 10 + "\n" + "-" * 10 + "Победил " + self.p2_name + "-" * 10


class GameLogic:
    def __init__(self):
        self.message = Message()
        self.mode = None
        self.player1 = None
        self.player2 = None
        self.p1_field = Field()
        self.p2_field = Field()
        self.grid = None
        self.ships = None
        self.winner = None

    @property
    def ch_mode(self):
        return self.mode

    @ch_mode.setter
    def ch_mode(self, m):
        if m not in ['1', '2']:
            raise UnexpectedValue
        else:
            self.mode = int(m)

    def mode_select(self):
        try:
            self.ch_mode = input()
        except UnexpectedValue as e:
            print(e)

    @property
    def get_grid(self):
        return self.grid

    @get_grid.setter
    def get_grid(self, grid_value):
        if grid_value not in ["6", "8", "10", "12", 6, 8, 10, 12]:
            raise UnexpectedValue
        else:
            self.grid = int(grid_value)

    def set_field_size(self):
        try:
            self.get_grid = input()
        except UnexpectedValue as e:
            print(e, "Размер ячеек может быть только 4, 6 или 8 ячеек")
        else:
            self.message.set_grid(self.grid)
            if self.grid in [6, 8]:
                self.ships = [3, 2, 2, 1, 1, 1, 1]
            elif self.grid == 10:
                self.ships = [3, 3, 2, 2, 1, 1, 1, 1, 1, 1]
            else:
                self.ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1]

    def add_players(self, second=False):
        if self.mode == 1:
            p1 = Player()
            p1.player_name = input()
            self.player1 = p1
            self.p1_field = Field(hidden=False)
            p2 = EnemyComputer()
            p2.name_constructor()
            self.player2 = p2
            self.message.set_names(self.player1.player_name, self.player2.player_name())
        else:
            if not second:
                p1 = Player()
                p1.player_name = input()
                self.player1 = p1
            else:
                p2 = Player()
                p2.player_name = input()
                self.player2 = p2
                self.message.set_names(self.player1.player_name, self.player2.player_name)

    def add_fields(self):
        self.p1_field.get_grid = self.grid
        self.p1_field.make_field()
        self.p2_field.get_grid = self.grid
        self.p2_field.make_field()
        self.message.set_fields(self.p1_field, self.p2_field)

    def place_ships(self, field):
        field.cleanup()
        for i in self.ships:
            ship = Ship(i)
            axis = randint(0, 1)
            for l in range(i):
                attemp = 1
                while True:
                    if attemp > 2000:
                        field.sucsess = False
                        break
                    if 0 < l:
                        pd = ship.dots[-1]
                        if axis == 0:
                            d = Dot(randint(pd.x - 1, pd.x + 1), pd.y)
                        else:
                            d = Dot(pd.x, randint(pd.y - 1, pd.y + 1))
                    else:
                        d = Dot(randint(0, self.grid-1), randint(0, self.grid-1))
                    if field.out(d) or d in field.busy:
                        attemp +=1
                        continue
                    else:
                        try:
                            ship.append_dot(Dot(d.x, d.y))
                        except CellIsBusy as e:
                            attemp +=1
                            continue
                        else:
                            break
            field.add_ship(ship)

    def shot(self, d, enemy_field):
            if d in enemy_field.shooten or enemy_field.out(d):
                raise CellIsBusy
            else:
                return d

    def aim(self, secomd = False):
        if not secomd:
            p = self.player1
            f = self.p2_field
        else:
            p = self.player2
            f = self.p1_field
        shot = None
        while shot is None:
            try:
                p.aim(self.grid)
            except UnexpectedValue as e:
                print(e)
                continue
            else:
                try:
                    shot = self.shot(p.shot, f)
                except CellIsBusy as e:
                    print(e)
                    continue
                else:
                    f.shot(shot)

    def check_winner(self):
        self.p1_field.check_loose()
        self.p2_field.check_loose()
        if self.p1_field.looser:
            self.winner = 2
        elif self.p2_field.looser:
            self.winner = 1


class ConsoleUI:
    def __init__(self):
        self.logic = GameLogic()
        self.message = self.logic.message

    def show_rules(self):
        print("Правила игры:")
        for i in self.message.rules():
            print(i)
        return ""

    def start_game(self):
        print(self.message.greeting())
        input()
        while self.logic.mode is None:
            print(self.message.choose_mode())
            self.logic.mode_select()
        if self.logic.mode == 1:
            print(self.message.input_name_p1())
            self.logic.add_players()
        else:
            print(self.message.input_name_p1())
            self.logic.add_players()
            print(self.message.input_name_p2())
            self.logic.add_players(second=True)
        print(self.message.vs())
        print()
        print()
        while self.logic.grid is None:
            print(self.message.field_size())
            self.logic.set_field_size()
        self.logic.add_fields()
        while True:
            self.logic.place_ships(self.logic.p1_field)
            if not self.logic.p1_field.sucsess:
                continue
            else:
                break
        while True:
            self.logic.place_ships(self.logic.p2_field)
            if not self.logic.p2_field.sucsess:
                continue
            else:
                break
        self.game_loop()

    def end_game(self):
        if self.logic.winner == 1:
            print(self.message.fields_update())
            print(self.message.splitter())
            print(self.message.winner())
        elif self.logic.winner == 2:
            print(self.message.fields_update(second=True))
            print(self.message.splitter())
            print(self.message.winner(second=True))

    def game_loop(self):
        row = 1
        while self.logic.winner is None:
            # ход первого игрока
            print("\n" * 50)
            print(self.message.vs())
            print(self.message.splitter())
            self.show_rules()
            print(self.message.splitter())
            print(self.message.row_number() + str(row))
            print(self.message.splitter())
            print(self.message.fields_update())
            print(self.message.move())
            self.logic.aim()
            self.logic.check_winner()
            print(self.message.hitmark())
            sleep(2)
            if self.logic.winner is not None:
                break
            #ход второго игрока
            print("\n" * 50)
            print(self.message.vs())
            print(self.message.splitter())
            self.show_rules()
            print(self.message.splitter())
            print(self.message.row_number() + str(row))
            print(self.message.splitter())
            print(self.message.fields_update(second=True))
            print(self.message.move(second=True))
            self.logic.aim(secomd=True)
            self.logic.check_winner()
            print(self.message.hitmark(second=True))
            row += 1
            sleep(2)
            continue
        print("\n" * 50)
        self.end_game()
        print(self.message.again())


class Main:
    def __init__(self):
        self.game = None

    def new(self):
        self.game = ConsoleUI()
        self.game.start_game()
        while True:
            try:
                self.restart()
            except UnexpectedValue as e:
                print(e)
                continue
            else:
                break

    def restart(self):
        _ = input()
        if _ in ['1', '2']:
            self.new()
        else:
            raise UnexpectedValue


if __name__ == "__main__":
    m = Main()
    m.new()
    