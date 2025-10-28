import sand as snd
from sea import create_sea


def create_beach():
    create_sea()
    snd.create_sand()
    print("this is a beach with a blue sea and yellow sand")