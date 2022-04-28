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
    return regex.sub(r'\p{C}', '', string)


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

    for log_path in logfiles:

        log_lines = open(log_path, 'r', encoding='utf-8',
                         errors='ignore').readlines()

        for line in log_lines:
            """# line = Mar 24 07:49:49 wlceventd:
            #        0            15 17
            line = line.replace('\n', '')
            shift = 0
            while shift < len(line) - 15:
                try:
                    t = datetime.strptime(
                        line[0 + shift:15 + shift], '%b %d %H:%M:%S').replace(year=log_year)
                    break
                except:
                    shift = shift + 1"""
            # remove \t \n or other control characters
            line = remove_control_characters(line)

            t = line.split()

            while(len(t) < 3):
                t.append('_')

            for i in (0, 1, 2):
                if t[i] == '':
                    t[i] == '_'
                if t[i][-1] == ':':
                    t[i] = t[i][:-1]
                t[i] = t[i].replace('[', '').replace(']', '')
            # put splitted log in to dict to separate each type of logs
            if t[0] not in log_type.keys():
                log_type[t[0]] = {}
            if t[1] not in log_type[t[0]].keys():
                log_type[t[0]][t[1]] = {}
            if t[2] not in log_type[t[0]][t[1]].keys():
                log_type[t[0]][t[1]][t[2]] = {}
                log_type[t[0]][t[1]][t[2]]['Count'] = 0
                log_type[t[0]][t[1]][t[2]]['log'] = line

            log_type[t[0]][t[1]][t[2]]['Count'] = \
                log_type[t[0]][t[1]][t[2]]['Count'] + 1

    # sort and count how many log in that type
    for t0 in log_type:
        for t1 in log_type[t0]:
            count = 0
            for t2 in log_type[t0][t1]:
                count = count + log_type[t0][t1][t2]['Count']
            # add line count after sorting
            log_type[t0][t1] = dict([('Count', count)] +
                                    sorted(log_type[t0][t1].items(), key=lambda x: x[1]['Count'], reverse=True))
        count = 0
        for t1 in log_type[t0]:
            count = count + log_type[t0][t1]['Count']
        log_type[t0] = dict([('Count', count)] +
                            sorted(log_type[t0].items(), key=lambda x: x[1]['Count'], reverse=True))
    count = 0
    for t0 in log_type:
        count = count + log_type[t0]['Count']
    log_type = dict([('Total log lines', count)] +
                    sorted(log_type.items(), key=lambda x: x[1]['Count'], reverse=True))
    # write result to file
    with open('logtype.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(log_type, file, Dumper=yaml.SafeDumper,
                  encoding='utf-8', sort_keys=False, indent=4, width=1000)
