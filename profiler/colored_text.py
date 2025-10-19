RESET_CODE = "\033[0m"


def rgb_from_hex(hex_color: str) -> tuple[int, int, int]:
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return r, g, b
    except ValueError:
        return None


def colored_text(text, *args) -> str:
    if len(args) == 3 and all(type(el) == int and 0 <= el <= 255 for el in args):
        r, g, b = args
        color_code = f"\033[38;2;{r};{g};{b}m"
    elif len(args) == 1 and type(args[0]) == str:
        r, g, b = rgb_from_hex(args[0])
        color_code = f"\033[38;2;{r};{g};{b}m"
        if color_code is None:
            return text
    else:
        return text
    return color_code + text + RESET_CODE


def colored_bg(text, *args) -> str:
    if len(args) == 3 and all(isinstance(el, int) and 0 <= el <= 255 for el in args):
        r, g, b = args
        bg_color_code = f"\033[48;2;{r};{g};{b}m"
    elif len(args) == 1 and type(args[0]) == str:
        r, g, b = rgb_from_hex(args[0])
        bg_color_code = f"\033[48;2;{r};{g};{b}m"
        if bg_color_code is None:
            return text
    else:
        return text
    return bg_color_code + text + RESET_CODE


def create_text_brush(hex_color: str) -> callable:
    def res(text):
        return colored_text(str(text), hex_color)
    return res


def create_bg_brush(hex_color: str) -> callable:
    def res(text):
        return colored_bg(str(text), hex_color)
    return res


def  text_color_code(hex_color: str) -> str:
    r, g, b = rgb_from_hex(hex_color)
    return f"\033[38;2;{r};{g};{b}m"

def  bg_color_code(hex_color: str) -> str:
    r, g, b = rgb_from_hex(hex_color)
    return f"\033[48;2;{r};{g};{b}m"


def create_brushes(hex_color: str) -> tuple[callable, callable]:
    return create_text_brush(hex_color), create_bg_brush(hex_color)


light_red, light_red_bg = create_brushes("FFC0C0")
red, red_bg = create_brushes("FF0000")
dark_red, dark_red_bg = create_brushes("C00000")

light_yellow, light_yellow_bg = create_brushes("FFFFC0")
yellow, yellow_bg = create_brushes("FFFF00")
dark_yellow, dark_yellow_bg = create_brushes("C0C000")

light_green, light_green_bg = create_brushes("C0FFC0")
green, green_bg = create_brushes("00FF00")
dark_green, dark_green_bg = create_brushes("00C000")

light_cyan, light_cyan_bg = create_brushes("C0FFFF")
cyan, cyan_bg = create_brushes("00FFFF")
dark_cyan, dark_cyan_bg = create_brushes("00C0C0")

light_blue, light_blue_bg = create_brushes("C0C0FF")
blue, blue_bg = create_brushes("0000FF")
dark_blue, dark_blue_bg = create_brushes("0000C0")

light_magenta, light_magenta_bg = create_brushes("FFC0FF")
magenta, magenta_bg = create_brushes("FF00FF")
dark_magenta, dark_magenta_bg = create_brushes("C000C0")

black = create_text_brush("000000")
black_bg = lambda text: text
white = lambda text: text
white_bg = create_bg_brush("FFFFFF")

orange, orange_bg = create_brushes("FFA500")