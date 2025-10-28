import sand
from beach import create_beach


def factorial(n):
    if n == 0:
        return 1
    x = 0
    for i in range(100000):
        x += i % 7
    return n * factorial(n - 1)


def fib(n):
    if n <= 2:
        return 1
    return fib(n - 1) + fib(n - 2)


def main():
    print(fib(25))
    print(factorial(5))
    print(factorial(6))
    print(factorial(7))

sand.pour_sand()
create_beach()
main()