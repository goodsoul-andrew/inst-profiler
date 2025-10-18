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
                    "ncalls": 0,
                    "prim_calls": 0,
                    "rec_depth": 0,
                    "tottime": 0.0,
                    "cumtime": 0.0,
                    "call_time": []
                }

            start_time = time.perf_counter()

            self.call_stack.append([func_name, start_time, 0])
            self.stat[func_name]["rec_depth"] += 1
            is_prim = self.stat[func_name]["rec_depth"] == 1
            if is_prim: self.stat[func_name]["prim_calls"] += 1

            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            name, start, children_time = self.call_stack.pop()
            elapsed_time = end_time - start
            clean_time = elapsed_time - children_time

            self.stat[func_name]["tottime"] += clean_time
            if is_prim:
                self.stat[func_name]["cumtime"] += elapsed_time
            self.stat[func_name]["rec_depth"] -= 1

            self.stat[func_name]["ncalls"] += 1
            self.stat[func_name]["call_time"].append(elapsed_time)

            if self.call_stack:
                self.call_stack[-1][2] += elapsed_time

            return result

        return wrapper

    def print_stat(self):
        print(f"{'ncalls':>9} {'tottime':>9} {'percall':>9} {'cumtime':>9} {'percall':>9} function")
        for k, v in self.stat.items():
            prim_calls = v["prim_calls"]
            ncalls = v["ncalls"]
            tottime = v["tottime"]
            percall1 = tottime / ncalls if ncalls else 0
            cumtime = v["cumtime"]
            percall2 = cumtime / prim_calls if prim_calls else 0
            if prim_calls != 1:
                print(f"{ncalls:7d}/{prim_calls} {tottime:9.6f} {percall1:9.6f} {cumtime:9.6f} {percall2:9.6f} {k}")
            else:
                print(f"{ncalls:9d} {tottime:9.6f} {percall1:9.6f} {cumtime:9.6f} {percall2:9.6f} {k}")


profiler = Profiler()


@profiler.profile
def factorial(n):
    if n == 0:
        return 1
    x = 0
    for i in range(100000):
        x += i % 7
    return n * factorial(n - 1)


@profiler.profile
def main():
    factorial(3)
    factorial(2)


if __name__ == "__main__":
    main()
    profiler.print_stat()
