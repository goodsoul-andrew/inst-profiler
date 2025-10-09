import functools
import time


class Profiler:
    def __init__(self):
        self.stat = {}

    def profile(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__qualname__
            if func_name not in self.stat:
                self.stat[func_name] = []
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            self.stat[func_name].append(elapsed_time)

            return result

        return wrapper


profiler = Profiler()


@profiler.profile
def sleep_func(n):
    time.sleep(n)


@profiler.profile
def one_func():
    return 1


if __name__ == "__main__":
    print("до:", profiler.stat)
    sleep_func(0.1)
    one_func()
    sleep_func(0.2)
    print("после:", profiler.stat)
