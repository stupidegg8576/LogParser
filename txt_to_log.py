# coding=utf-8

import sys
import os
from datetime import datetime
import re
import yaml


class log():

    def __init__(self, log_type, log_time) -> None:
        self.type = log_type
        self.time = log_time
        self.content = ''


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

        log_lines = open(log_path, 'r', encoding='utf-8',
                         errors='ignore').readlines()
        log_year = datetime.fromtimestamp(os.path.getmtime(log_path)).year

        for line in log_lines:
            # line = Mar 24 07:49:49 wlceventd:
            #        0            15 17
            line = line.replace('\n', '')
            shift = 0
            while shift < len(line) - 15:
                try:
                    t = datetime.strptime(
                        line[0 + shift:15 + shift], '%b %d %H:%M:%S').replace(year=log_year)
                    break
                except:
                    shift = shift + 1

            t = line[16+shift:].split(':')
            for i in range(len(t)):
                if '[' in t[i]:
                    t[i] = t[i].split('[')[0] + '[]'
            if t[0] == '':
                t[0] = ' '
            if t[0] not in log_type.keys():
                log_type[t[0]] = {}
            if len(t) > 2:
                if t[1] not in log_type[t[0]].keys():
                    log_type[t[0]][t[1]] = line[16+shift:].replace('\n', '')
    print(log_type)
    with open('logtype.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(log_type, file, Dumper=yaml.SafeDumper,
                  encoding='utf-8', sort_keys=False)
