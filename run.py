from fastapi import FastAPI
from pydantic import BaseModel
from core import Game
import traceback

app = FastAPI()

class CreateGame(BaseModel):
    bot_code_1: str
    bot_code_2: str


def get_def(code: str):
    param = {}
    exec(code, param)
    for item in param.values():
        if callable(item):
            return item

@app.post('/game/')
async def new_game(data: CreateGame):
    try:
        game = Game()
        bot1 = get_def(data.bot_code_1)
        bot2 = get_def(data.bot_code_2)
        str_out = ''
        for _ in range(100):

            # ход игрока 1
            log = game.right.fire(*bot1(game.right))
            str_out += f"Выстрелил игрок 1: {log}\n"

            if all(ship.is_destruction for ship in game.right.ships):
                str_out += "Поздравления от Фёдора! Победил игрок 1\n"
                break

            # ход игрока 2
            log = game.left.fire(*bot2(game.left))
            str_out += f"Выстрелил игрок 2: {log}\n"

            if all(ship.is_destruction for ship in game.left.ships):
                str_out += "Поздравления от Фёдора! Победил игрок 2\n"
                break
        else:
            str_out == "Ничья!"
        
        return str_out
    except Exception as ex:
        return str(traceback.format_exc())