from core import Field
import requests
import inspect

url = 'http://127.0.0.1:8000/game/'

def bot1(field):
    for ship in field.ships:
        for point in ship.points:
            if not point.is_destruction:
                return point.row, point.col
    import random
    return random.randint(1, 9), random.randint(1, 9)


def bot2(field):

    import random
    return random.randint(1, 9), random.randint(1, 9)

body = {
    'bot_code_1' :  inspect.getsource(bot1),
    'bot_code_2' :  inspect.getsource(bot2),
}

text = requests.post(url, json=body).text
print(type(text))
for line in text.split('\\n'):
    print(line)