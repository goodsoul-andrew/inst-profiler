import collections
import os
from dataclasses import dataclass, field
from math import floor
from xml.sax import parse

from .colored_text import black, red_bg, yellow_bg, orange_bg, bg_color_code, text_color_code, RESET_CODE

COLORS = [bg_color_code("FF0000"), bg_color_code("FFA500"), bg_color_code("FFFF00"), bg_color_code("FFFFC0")]
black_text_code = text_color_code("000000")

def next_color(parent_color: int, last_child_color: int = -1):
    if last_child_color == -1:
        for i in range(len(COLORS)):
            if i != parent_color:
                return i
    else:
        colors_nums = list(range(len(COLORS)))
        ind = last_child_color
        while colors_nums[ind] == last_child_color or colors_nums[ind] == parent_color:
            ind = (ind + 1) % len(COLORS)
        return colors_nums[ind]


@dataclass
class FlameGraph:
    name: str
    start: float
    end: float
    elapsed_time: float = field(init=False)
    children: list["FlameGraph"] = field(default_factory=list)
    parent: "FlameGraph" = None
    str_length: int = 0
    str_start: int = 0
    level: int = 0
    color: int = 0

    def __post_init__(self):
        self.elapsed_time = self.end - self.start

    def add_child(self, new_child: "FlameGraph"):
        if self.children:
            last_child = self.children[-1]
            if new_child.start >= last_child.start and new_child.end <= last_child.end:
                self.children[-1].add_child(new_child)
            elif new_child.start >= last_child.start and new_child.end > last_child.end:
                new_child.parent = self
                new_child.level = self.level + 1
                new_child.color = next_color(self.color, self.children[-1].color)
                new_child.str_length = floor(self.str_length * new_child.measure)
                new_child.str_start = last_child.str_end
                # print(new_child.name, new_child.measure, new_child.str_length)
                self.children.append(new_child)
                # self.update_str_length()
        else:
            new_child.parent = self
            new_child.level = self.level + 1
            new_child.str_length = floor(self.str_length * new_child.measure)
            new_child.str_start = self.str_start
            new_child.color = next_color(self.color)
            # print(new_child.name, new_child.parent.name, new_child.measure, floor(self.str_length * self.measure), new_child.str_length)
            self.children.append(new_child)

    @property
    def measure(self):
        if self.parent:
            return self.elapsed_time / self.parent.elapsed_time
        return 1

    @property
    def str_end(self):
        return self.str_start + self.str_length

    @staticmethod
    def make_tree(total_time: float, data: list[dict[str, str | float]]) -> "FlameGraph":
        data = sorted(data, key=lambda x: (x["start"], x["end"]))
        tree = FlameGraph("program", 0, total_time, [])
        tree.str_length = os.get_terminal_size().columns
        for el in data:
            tree.add_child(FlameGraph(el["name"], el["start"], el["end"], []))
        return tree

    def colored_name_list(self) -> list[str]:
        res = ""
        if self.str_length == 0:
            return []
        if len(self.name) < self.str_length:
            res =  self.name + " " * (self.str_length - len(self.name))
        else:
            res =  self.name[:self.str_length - 1] + " "
        res = list(res)
        res[0] = COLORS[self.color] + black_text_code + res[0]
        res[-1] += RESET_CODE
        return res

    def __iter__(self):
        stack = [self]
        return FlameGraphIterator(stack)

    @staticmethod
    def build_flame_graph(total_time: float, data: list[dict[str, str | float]]):
        width = os.get_terminal_size().columns
        tree = FlameGraph.make_tree(total_time, data)
        result = []
        for curr in tree:
            # print(curr.name, curr.level, curr.measure, curr.str_start, curr.str_length)
            curr_str = curr.colored_name_list()
            if curr.level + 1 > len(result):
                result.append([" "] * width)
            for i in range(curr.str_start, curr.str_start + curr.str_length):
                # print(i, curr.str_start)
                result[curr.level][i] = curr_str[i - curr.str_start]
        return ["".join(line) for line in result if any([el != " " for el in line])][::-1]


class FlameGraphIterator:
    def __init__(self, stack: list[FlameGraph]):
        self.stack = stack

    def __next__(self):
        if not self.stack:
            raise StopIteration
        current_node = self.stack.pop()
        for child in current_node.children:
            self.stack.append(child)
        return current_node

    def __iter__(self):
        return self