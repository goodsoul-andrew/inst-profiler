import time
import quartz
from quartz import create_quartz


def create_sand():
    create_quartz()
    print("create sand from quartz")


def pour_sand():
    create_sand()
    create_sand()
    time.sleep(0.01)


