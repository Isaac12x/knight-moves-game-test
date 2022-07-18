TEXT_BLACK = "\033[30m"
BACKGROUND_RED = "\033[41m"
BACKGROUND_GREEN = "\033[42m"
BACKGROUND_YELLOW = "\033[43m"
BACKGROUND_BLUE = "\033[44m"
RESET = "\033[m"

class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class NestedDotDict(DotDict):
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            self[key] = value

def cli_sep(lines: int):
    [print("") for _ in range(0,lines)]

def cli_lines(labove:int=None, lbelow:int=None):
    # TODO: @improvements -> flexibility: accept cli_lines(num) and add numlines above and below
    if labove:
        cli_sep(labove)
    print("=======================")
    cli_sep(lbelow) if lbelow else cli_sep(1)
    

def pposition(item):
    print("|", end="", flush=True)
    print(TEXT_BLACK, BACKGROUND_YELLOW, f"{item}", RESET, "", end="", flush=True)

def ppossible(item):
    print("|", end="", flush=True)
    print(TEXT_BLACK, BACKGROUND_GREEN, f"{item}", RESET, "",  end="", flush=True)
