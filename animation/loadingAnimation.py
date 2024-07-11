import os
import time
import sys
import random

from utils import clear_screen

MAX_HORIZONTAL = 16
MAX_VERTICAL = 7


def generate_frame(horizontal_position, vertical_position):
    empty_line ="|                                            |\n"
    frame = (
        "---------------------------------------------\n"
        "|           MED Project - Scanning...       |\n"
        "---------------------------------------------\n"
        f"{empty_line * (vertical_position)}"
        f"|{' ' * (horizontal_position)}   ___     _____      ___   {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)} /    `  .`      `.  '    \\ {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}|     / /          \\ \\     |{' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}|    | |  .-.  .-.  | |    |{' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}`    \\ \\            / /    '{' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)} \\    `\\ \\        / /'    / {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}  `. _  \\ \\      / /  _ .'  {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}     _/  | |    | |  \\_     {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}    `---'  /   /   `---'    {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}        .-`  ,`             {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"|{' ' * (horizontal_position)}        `---`               {' ' * (MAX_HORIZONTAL - horizontal_position)}|\n"
        f"{empty_line * (MAX_VERTICAL - vertical_position)}"
        "---------------------------------------------\n"
    )
    return frame


def clear_screen_lines(lines):
    # Move the cursor up for the number of lines and clear each line
    for _ in range(lines):
        sys.stdout.write("\033[F\033[K")


def loading_screen(thread):
    horizontal_position = random.randint(0, MAX_HORIZONTAL)
    horizontal_direction = random.choice([1, -1])
    vertical_position = random.randint(0, MAX_VERTICAL)
    vertical_direction = random.choice([1, -1])

    # Calculate the number of lines in the frame
    lines_in_frame = generate_frame(0, 0).count('\n')
    clear_screen()
    while thread.is_alive():
        if vertical_position == MAX_VERTICAL:
            vertical_direction = -1
        if vertical_position == 0:
            vertical_direction = 1
        if horizontal_position == MAX_HORIZONTAL:
            horizontal_direction = -1
        if horizontal_position == 0:
            horizontal_direction = 1
        frame = generate_frame(horizontal_position, vertical_position)
        print(frame, end='')
        time.sleep(0.3)
        clear_screen_lines(lines_in_frame)
        horizontal_position += horizontal_direction
        vertical_position += vertical_direction
