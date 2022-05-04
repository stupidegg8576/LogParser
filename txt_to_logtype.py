import regex
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


def remove_control_characters(string):
    return regex.sub(r'[\p{C}\[\]\(\)]', '', string)


def load_func_parse_data(path):
    try:
        file = open(path, 'r')
    except IOError:
        raise IOError("Load function parse data Yaml file failed")
    return yaml.load(file, Loader=yaml.FullLoader)


if __name__ == '__main__':

    # get files list
    logfloder_path = './TracelineLog/'
    logfiles = []
    for model_name in os.listdir(logfloder_path):
        for report_ID in os.listdir(logfloder_path + model_name):
            if os.path.exists(logfloder_path + model_name + '/' + report_ID + '/syslog.log'):
                logfiles.append(logfloder_path + model_name +
                                '/' + report_ID + '/syslog_replaced.log')

    log_type = {}
    max_len = 0
    max_len_str = ''
    for log_path in logfiles:

        log_lines = open(log_path, 'r', encoding='utf-8',
                         errors='ignore').readlines()
        for line in log_lines:
            line = remove_control_characters(line)
            splited_line = re.split('[: ,]+', line)
            if len(splited_line) > max_len:
                max_len = len(splited_line)
                max_len_str = splited_line
            temp = log_type
            for i in range(len(splited_line)):
                if splited_line[i] not in temp.keys():
                    temp[splited_line[i]] = {}
                temp = temp[splited_line[i]]

    log_type = dict(sorted(log_type.items(), key=lambda x: x[0], reverse=True))
    print(max_len)
    print(max_len_str)
    # write result to file
    with open('logtype.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(log_type, file, Dumper=yaml.SafeDumper,
                  encoding='utf-8', sort_keys=False, indent=4, width=1000)
