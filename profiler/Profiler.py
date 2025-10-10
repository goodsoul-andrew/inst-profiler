import functools
import time


class Profiler:
    def __init__(self):
        self.stat = {}
        self.call_stack = []

    def profile(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__qualname__
            if func_name not in self.stat:
                self.stat[func_name] = {
                    "calls": 0,
                    "call_time": [],
                    "clean_time": 0.0,
                    "cumulative_time": 0.0
                }

            start_time = time.perf_counter()
            self.call_stack.append([func_name, start_time, 0])
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            name, start, children_time = self.call_stack.pop()
            elapsed_time = end_time - start
            clean_time = elapsed_time - children_time

            self.stat[func_name]["calls"] += 1
            self.stat[func_name]["call_time"].append(elapsed_time)
            self.stat[func_name]["cumulative_time"] += elapsed_time
            self.stat[func_name]["clean_time"] += clean_time

            if self.call_stack:
                self.call_stack[-1][2] += elapsed_time

            return result

        return wrapper


profiler = Profiler()


@profiler.profile
def parent_func():
    time.sleep(0.1)
    child_func()
    time.sleep(0.1)


@profiler.profile
def child_func():
    time.sleep(0.2)


if __name__ == "__main__":
    print("до:", profiler.stat)
    parent_func()
    child_func()
    print("после:", profiler.stat)
