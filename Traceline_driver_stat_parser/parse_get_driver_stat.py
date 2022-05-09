import regex
import os
import json


def remove_control_characters(string):
    return regex.sub(r'\p{C}', '', string)


if __name__ == '__main__':
