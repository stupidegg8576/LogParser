import sys
import os
from datetime import datetime
import re
from traceback import print_tb
import yaml


class log():

    def __init__(self, log_type, log_time) -> None:
        self.type = log_type
        self.time = log_time


def load_func_parse_data(path):
    try:
        file = open(path, 'r')
    except IOError:
        raise IOError("Load function parse data Yaml file failed")
    return yaml.load(file, Loader=yaml.FullLoader)


def log_time(line):
    try:
        time = datetime.strptime(
            line[:15], '%b %d %X').replace(year=2022)
    except:
        time = datetime.fromtimestamp(0)
    return time


def log_format(line):
    temp = ''
    last_is_digit = False
    in_brackets = False

    for char in line[16:]:

        if char in '[({':
            in_brackets = True
        elif char in '])}':
            in_brackets = False

        # remove space in brackets
        if char == ' ' and in_brackets == True:
            pass
        elif char.isdigit() and not last_is_digit:
            temp += char
            last_is_digit = True

        elif not char.isdigit():
            temp += char
            last_is_digit = False
    return temp


if __name__ == '__main__':

    func_parse_data = load_func_parse_data('./text2log_func_parse_data.yaml')

    # get files list
    logfloder_path = './TracelineLog/'
    logfiles = []
    for model_name in os.listdir(logfloder_path):
        for report_ID in os.listdir(logfloder_path + model_name):
            if os.path.exists(logfloder_path + model_name + '/' + report_ID + '/syslog.log'):
                logfiles.append(logfloder_path + model_name +
                                '/' + report_ID + '/syslog.log')

    log_type = {}

    for log_path in logfiles:

        log = open(log_path, 'r', encoding='utf-8',
                   errors='ignore').readlines()

        for line in log:
            # line = Mar 24 07:49:49 wlceventd:
            #        0            15 17
            if 'get radar signal' in line:
                print(line)
