import random as rnd
import json
from enum import Enum

class Emoji(str, Enum):
    ship = '🚢'
    hurt = '🔻'
    kill = '💀'
    blunder = '◽'
    field = '🟦'

class Point:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_destruction = False

    @classmethod
    def from_dict(cls, data):
        point = cls(data['row'], data['col'])
        point.is_destruction = data.get('is_destruction', False)
        return point

    def to_dict(self):
        return {
            'row': self.row,
            'col': self.col,
            'is_destruction': self.is_destruction
        }
            
    def __str__(self):
        return f"{Emoji.ship}/{self.col}"
    
    def __repr__(self):
        return str(self)

class Ship:
    def __init__(self):
        self.points: list[Point] = []
        self.is_destruction = False

    @classmethod 
    def from_dict(cls, data):
        ship = cls()
        for point_data in data['points']:
            ship.add_point(Point.from_dict(point_data))
        ship.is_destruction = data.get('is_destruction', False)
        return ship
          
    def to_dict(self):
        return {
           'points': [point.to_dict() for point in self.points],
           'is_destruction': self.is_destruction
        }

    def add_point(self, point: Point):
        self.points.append(point)

    def __str__(self):
        return f'{Emoji.ship}{self.points}'
    
    def __repr__(self):
        return str(self)

class Field:
    def __init__(self, size: int = 10):
        self.ships: list[Ship] = []
        self.size = size
        self.blunders: list[Point] = []

    @classmethod
    def from_dict(cls, data):
        field = cls()
        field.size = data['size']
        for ship_data in data['ships']:
            field.ships.append(Ship.from_dict(ship_data))
        return field

    def to_dict(self):
        return {
            'size': self.size,
            'ships': [ship.to_dict() for ship in self.ships]
        }

    def add_ship(self, count: int):
        ignore_point = set()
        for ship in self.ships:
            for p in ship.points:
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        ignore_point.add((p.row + dr, p.col + dc))

        candidate = []
        
        for row in range(self.size):
            for col in range(self.size - count + 1):
                ship = Ship()
                for i in range(count):
                    ship.add_point(Point(row, col + i))
                check = all((p.row, p.col) not in ignore_point for p in ship.points)
                if check:
                    candidate.append(ship)

        for row in range(self.size - count + 1):
            for col in range(self.size):
                ship = Ship()
                for i in range(count):
                    ship.add_point(Point(row + i, col))
                check = all((p.row, p.col) not in ignore_point for p in ship.points)
                if check:
                    candidate.append(ship)

        if not candidate:
            return None

        chosen = rnd.choice(candidate)
        self.ships.append(chosen)
        return chosen

    def __str__(self):
        grid = [[Emoji.field for _ in range(self.size)] for _ in range(self.size)]
        for ship in self.ships:
            for point in ship.points:
                r, c = point.row, point.col
                if point.is_destruction:
                    if not ship.is_destruction:
                        grid[r][c] = Emoji.hurt
                    else:
                        grid[r][c] = Emoji.kill
                else:
                    grid[r][c] = Emoji.ship
        for blunder in self.blunders:
            grid[blunder.row][blunder.col] = Emoji.blunder
        return "\n".join(" ".join(row) for row in grid)
    
    def __repr__(self):
        return str(self)

    def fire(self, row_ind, col_ind):
        for ship in self.ships:
            is_destruction = False
            for point in ship.points:
                if row_ind == point.row and col_ind == point.col:
                    point.is_destruction = True
                    is_destruction = True
                    break
            if is_destruction:
                points_bool = [point.is_destruction for point in ship.points]
                if all(points_bool):
                    ship.is_destruction = True
                    return 'Убил!   💀💀💀'
                else:
                    return 'Попал!  🔥🔥🔥'
        self.blunders.append(Point(row_ind, col_ind))
        return 'Мимо  :('

class Game:
    def __init__(self, load_file: str = None):
        self.left = Field()
        self.right = Field()
        self.shot_set = set()
        self.hunt = []

        if load_file is None:
            for ship_size in [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]:
                self.left.add_ship(ship_size)
                self.right.add_ship(ship_size)
        else:
            self.load_from_file(load_file)

    def save_to_file(self, file_name: str = "data.json"):
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(
                obj=[self.left.to_dict(), self.right.to_dict()],
                fp=f,
                ensure_ascii=False,
                indent=4
            )

    def load_from_file(self, file_name: str = 'data.json'):
        with open(file_name, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            self.left = Field.from_dict(loaded_data[0])
            self.right = Field.from_dict(loaded_data[1])

    def print_fields(self):
        result = ''
        for line1, line2 in zip(str(self.left).split('\n'), str(self.right).split('\n')):
            line2 = line2.replace(Emoji.ship, Emoji.field)
            result += f'{line1}\t\t{line2}\n'
        return result
