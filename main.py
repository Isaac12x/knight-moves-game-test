# Possibility to extend the game by adding an adversary and take turns.

import copy
import json
import math
import os
import platform
import random
import string
import sys
import signal

from statistics import mean
from itertools import accumulate
from utils import (
    NestedDotDict,
    cli_sep,
    cli_lines,
    pposition,
    ppossible,
    BACKGROUND_YELLOW,
    TEXT_BLACK,
    RESET,
    BACKGROUND_RED,
)


def print_board(
    gameboard,
    gameboard_repr,
    cmd_history,
    cols=5,
    rows=4,
    current_pos: int = None,
    possible_idxs: [int] = None,
):
    def print_board_line(snap, current_pos: int = None, possible_idxs: [int] = None):
        for item in snap:
            if item == None:
                print("|     ", end="", flush=True)
                continue
            if current_pos and gameboard[item] == current_pos:
                pposition(item)
                continue
            if possible_idxs and gameboard[item] in possible_idxs:
                ppossible(item)
                continue
            print(f"|  {item}  ", end="", flush=True)

        print("|")

    cli_lines(1, 0)
    print("Your moves: ", cmd_history)
    print("")
    print("", "—" * (cols * rows))
    [print_board_line(each, current_pos, possible_idxs) for each in gameboard_repr]
    print("", "—" * (cols * rows))


def make_gameboard(
    letter_rows=3, columns=5, number_rows=1, number_per_row=3, skipped_num_idxs=[15, 19]
):
    total_indexes = [
        x
        for x in range((letter_rows + number_rows) * columns)
        if x not in skipped_num_idxs
    ]
    numbers = [str(x) for x in range(1, number_per_row + 1)]
    values = [
        each for each in string.ascii_uppercase[: (letter_rows * columns)]
    ] + numbers
    game = {
        letter: index for letter, index in zip(values, total_indexes)
    }  # as {"A": 0, "B": 1 ...}
    return game


def count_vowels(sequence):
    occurrences = 0
    for each in ["a", "e", "i", "o", "u"]:
        occurrences += sequence.lower().count(each)
    return occurrences


def has_too_many_vowels(sequence, path, max_vowels=2):
    # NOTE: what you're interested in
    if len(path) > 3:  # we shouldn"t see this but.
        print("Something is wrong with your selection")
    occurrences = count_vowels(sequence + path)
    if occurrences >= max_vowels:
        return True
    return False


def possible_moves(current_pos, gameboard, boundries) -> dict:
    # NOTE: what you're interested in
    def make_ids(op_gameboard, current_pos, operands, boundries):
        non_idxs = [15, 19]
        next_pos_index = sum(operands) + current_pos
        transformed = list(accumulate(operands))
        if (
            next_pos_index > 20 or next_pos_index in non_idxs
            or crosses_boundry(boundries, current_pos, transformed)
        ):
            return
        try:
            return {
                "".join(
                    [op_gameboard[current_pos + t] for t in transformed]
                ): next_pos_index
            }
        except KeyError:
            return

    opposite_gameboard = {v: k for k, v in gameboard.items()}
    possible_idx_raw = [
        [5, 5, 1],
        [5, 5, -1],
        [-5, -5, +1],
        [-5, -5, -1],
        [1, 1, 5],
        [1, 1, -5],
        [-1, -1, 5],
        [-1, -1, -5],
    ]
    possible_idxs = list(
        filter(
            None,
            [
                make_ids(opposite_gameboard, current_pos, each, boundries)
                for each in possible_idx_raw
            ],
        )
    )
    possible_idxs = {k: v for d in possible_idxs for k, v in d.items()}
    valid_idxs = {
        seq: idx for seq, idx in possible_idxs.items() if idx in gameboard.values()
    }
    return valid_idxs


def make_all_possible_seqs(gameboard, boundries, allowed_next, current_pos=None):
    # NOTE: what you're interested in, better implemented in a tree structure
    # FIXME: if more time, I would like to also improve efficiency by abstraction
    #        as right now it's a bit difficult to understand at a glance
    def test_length(seq):
        if len(seq) == 10:
            return True
        return False
    def log_enabled(alist, key, enabled=False):
        if enabled:
            alist.pop(key)
            print(f"Missing cycles: {len(list(alist.values()))}")

    left_to_test = copy.deepcopy(allowed_next)
    accumulated_next = {}

    for k, v in allowed_next.items():
        next_moves = possible_moves(v, gameboard, boundries)
        joined_paths = [
            f"{current_pos if current_pos else ''}{k}{move}"
            for move in next_moves.keys()
        ]
        joined_path_idx_dict = {
            path: v
            for path, (k, v) in zip(joined_paths, next_moves.items())
            if path.endswith(k)
        }
        accumulated_next = {**accumulated_next, **joined_path_idx_dict}
        log_enabled(left_to_test, k)

    if all([test_length(itm) for itm in list(accumulated_next.keys())]):
        return list(accumulated_next.keys())
    return make_all_possible_seqs(gameboard, boundries, accumulated_next)


def reset(**kwargs):
    def default_reset():
        keypress = None
        sequence = ""
        seq_len = 0

    opts = ["k", "s", "l"]
    if any(item in opts for item in kwargs):
        # I know this can be done better, but I"m a bit constrained in time
        # and declarative coding is the quickest!
        try:
            kwargs["k"]
            keypress = None
        except TypeError:
            pass

        try:
            kwargs["s"]
            sequence = ""
        except TypeError:
            pass

        try:
            kwargs["l"]
            seq_len = 0
        except TypeError:
            pass

    else:
        default_reset()


def transform_board(gameboard, cols=5, rows=4):
    # TODO: refine so the insertion is at position where there is a gap
    its = list(gameboard.keys())
    its.insert(15, None)
    its.append(None)
    slices = [
        its[each * 5 : each * 5 + 5] for each in range(0, math.floor(len(its) / cols))
    ]
    return slices


def make_board_boundries(gameboard,gameboard_repr):
    lb = [each[0] for each in gameboard_repr if each[0]]
    rb = [each[-1] for each in gameboard_repr if each[-1]]
    return [gameboard[itm] for itm in [*lb, *rb]]


def crosses_boundry(board_boundries, current_pos, fsum):
    for i, itm in enumerate(fsum):
        if current_pos in board_boundries and current_pos + itm in board_boundries:
            return True
        if current_pos + itm in board_boundries and (i + 1) <= 2:
            if current_pos + fsum[i + 1] in board_boundries:
                return True
    return False

def reinput():
    cli_lines(labove=2, lbelow=0)
    print(msg.gameplay.prompt)
    choice = input("> ")
    return choice

def main():
    keypress = None
    sequence = ""
    seq_len = 10
    cmd_history = ""

    current_pos = None
    allowed_next = None
    start_pos = None
    all_responses = None
    gameboard = make_gameboard()
    gameboard_repr = transform_board(gameboard)
    board_boundries = make_board_boundries(gameboard, gameboard_repr)
    reserved_word_commands = ["reset", "exit", "responses"]
    
    # gameplay, show only at the beginning
    print(msg.start.welcome, msg.start.goal, msg.start.rules, sep=os.linesep)
    print_board(gameboard, gameboard_repr, cmd_history)

    ptfm = platform.system()
    if ptfm.casefold() == "windows".casefold():
        os.system("pause")
    else:
        os.system("/bin/bash -c 'read -s -n 1 -p \"Press any key to start...\"'")

    start_pos = random.choice(sorted(list(gameboard.values())))
    current_pos = start_pos
    allowed_next = possible_moves(current_pos, gameboard, board_boundries)
    all_sequences = make_all_possible_seqs(
        gameboard,
        board_boundries,
        allowed_next,
        next(key for key, value in gameboard.items() if value == current_pos),
    )
    while not keypress and len(sequence) <= 10:  # core loop
        cli_lines(labove=2, lbelow=1)
        print_board(
            gameboard,
            gameboard_repr,
            cmd_history,
            current_pos=current_pos,
            possible_idxs=allowed_next.values(),
        )

        print(msg.gameplay.prompt)
        print(msg.gameplay.prompt_hints)
        choice = input("> ")
        
        if choice in reserved_word_commands:
            if choice == "reset":
                reset()
                choice = reinput()
            if choice == "exit":
                sys.exit(0)
            if choice == "responses":
                print("Here all possible paths: ", ", ".join(all_sequences))
                choice = reinput()

        if len(choice) > 1:
            print(TEXT_BLACK, BACKGROUND_RED, msg.errors.max_keys, RESET)
            print(msg.gameplay.retry)
            choice = reinput()
        else:  # core
            if choice.upper() in gameboard.keys():
                choice_idx = gameboard[choice.upper()]
                if choice_idx in allowed_next.values():
                    reversed_allowed_choices = {v: k for k, v in allowed_next.items()}
                    selected_choice = reversed_allowed_choices[choice_idx]
                    if not has_too_many_vowels(sequence, selected_choice):
                        cmd_history += choice
                        current_pos = choice_idx
                        sequence += selected_choice
                        allowed_next = possible_moves(
                            current_pos, gameboard, board_boundries
                        )
                        print(
                            TEXT_BLACK,
                            BACKGROUND_YELLOW,
                            f"You pressed {choice}",
                            RESET,
                        )
                    else:
                        print(
                            TEXT_BLACK,
                            BACKGROUND_RED,
                            f"Too many vowels in your sequence",
                            RESET,
                        )
                else:
                    print(TEXT_BLACK, BACKGROUND_RED, f"Not a valid move", RESET)
            else:
                print(
                    TEXT_BLACK,
                    BACKGROUND_RED,
                    f"Location not in board or not valid key",
                    RESET,
                )

    if len(sequence) >= seq_len:  # ends nicely
        cli_lines(labove=0, lbelow=1)
        print(f"Your sequence: {sequence}")
        print(msg.finish.done)

        num_vowels = count_vowels(sequence)
        if num_vowels == 0:
            print(msg.finish.success)
        if num_vowels == 1:
            print(msg.finish.vowel)
        if num_vowels == 2:
            print(msg.finish.vowels)
        cli_lines(labove=0, lbelow=2)

        print(msg.finish.replay)
        inp = input(" ")

        if inp == "y":
            reset()
            # TODO: add execute loop again
        else:
            print(msg.finish.goodbye)
            sys.exit(0)


def terminate():
    print(msg.exit.smile, msg.exit.bye, sep="\n")
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


if __name__ == "__main__":
    msging_str = open("./messaging.json", "r").read()
    msg = NestedDotDict(json.loads(msging_str))

    main()
    signal.signal(signal.SIGTERM, terminate())
