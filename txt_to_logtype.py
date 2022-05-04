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
    # remove \n \t [ ] ( )....
    return regex.sub(r'[\p{C}\[\]\(\)]', '', string)


def load_func_parse_data(path):
    try:
        file = open(path, 'r')
    except IOError:
        raise IOError("Load function parse data Yaml file failed")
    return yaml.load(file, Loader=yaml.FullLoader)


if __name__ == '__main__':

    # load replace yaml
    replace_yaml_file = open('txt_replace.yaml', 'r', encoding='utf-8')
    model_list_file = open('model_list.yaml', 'r', encoding='utf-8')
    replace_yaml = yaml.load(replace_yaml_file, yaml.CFullLoader)
    model_list = yaml.load(model_list_file, yaml.CFullLoader)

    INPUT_DATA_TYPE = 'raw_log_by_type'
    # get files list
    logfloder_path = './TracelineLog/'
    logfiles = []
    # TracelineLog \ model_name \ report_ID
    if INPUT_DATA_TYPE == 'traceline_log':
        for model_name in os.listdir(logfloder_path):
            for report_ID in os.listdir(logfloder_path + model_name):
                if os.path.exists(logfloder_path + model_name + '/' + report_ID + '/syslog.log'):
                    logfiles.append(logfloder_path + model_name +
                                    '/' + report_ID + '/syslog_replaced.log')

    # raw_log_by_type.txt
    # smaller and non repeating data set
    if INPUT_DATA_TYPE == 'raw_log_by_type':
        log_paths = ['raw_log_by_type.txt']

    log_type = {}

    for log_path in logfiles:

        log_lines = open(log_path, 'r', encoding='utf-8',
                         errors='ignore').readlines()
        for line in log_lines:
            line = remove_control_characters(line)
            # split words by ': ,'
            splited_line = re.split('[: ,]+', line)

            # store log by word to dict recursively
            temp = log_type
            for i in range(len(splited_line)):
                if splited_line[i] not in temp.keys():
                    temp[splited_line[i]] = {}
                temp = temp[splited_line[i]]
    # sort by char
    log_type = dict(sorted(log_type.items(), key=lambda x: x[0], reverse=True))

    # write result to yaml file
    with open('logtype.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(log_type, file, Dumper=yaml.SafeDumper,
                  encoding='utf-8', sort_keys=False, indent=4, width=1000)
