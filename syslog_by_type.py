import os
import yaml
import regex
from datetime import datetime
import sys
import getopt


def remove_control_characters(string):
    return regex.sub(r'\p{C}', '', string)


def combine_time_log(log_times, log_lines):
    for i in range(len(log_lines)):
        log_lines[i] = log_times[i].strftime(
            r'%b %d %H:%M:%S ') + log_lines[i]
    return log_lines


def split_time_from_log(log_lines, year='2022'):
    log_times = []
    for i in range(len(log_lines)):
        # find time in log
        # sometimes it will contain some noise at the front of log
        log_shift = 0
        time_search = regex.search(
            '[0-9] ([0-9]{2}:){2}[0-9]{2} ', log_lines[i])
        if time_search != None:
            log_shift = time_search.span()[1]
            # split log_lines to log_time and log_lines
            log_times.append(datetime.strptime(
                year + log_lines[i][log_shift-16:log_shift], r'%Y%b %d %H:%M:%S '))
            log_lines[i] = log_lines[i][log_shift:]
        else:
            log_times.append(None)
    return log_times, log_lines


def correct_log_times(log_times):
    for i in range(len(log_times)-1):
        if log_times[i].month == 5 and log_times[i] - log_times[i+1]:
            pass
    return


def remove_useless_char(log_lines):
    for i in range(len(log_lines)):
        # remove control chars
        log_lines[i] = remove_control_characters(log_lines[i])

        # remove matched chars
        for rule in remove_yaml:
            log_lines[i] = regex.sub(
                remove_yaml[rule]['regex'], remove_yaml[rule]['replace'], log_lines[i])

    return log_lines


"""def replace_keywords(log_lines):

    for i in range(len(log_lines)):
        # replace model_name: model should be replace before keywords
        for model in model_list:
            # model names have a lot of variants,
            # so consider model_name**** as a model_name too
            log_lines[i] = regex.sub(
                r'(?i)' + model + '([0-9A-Za-z_-]{0,})', '|_MODEL_NAME|', log_lines[i])

        # replace keywords
        for rule in replace_yaml:
            log_lines[i] = regex.sub(
                replace_yaml[rule]['regex'], replace_yaml[rule]['replace'], log_lines[i])
    return log_lines"""


def log_separate_by_type(log_lines, log_type):
    log_lines_by_type = []

    l = log_type.__len__()

    for line in log_lines:
        t = line[16:16+l]
        if t == log_type:
            log_lines_by_type.append(line + '\n')

    return log_lines_by_type


def txt_to_log_type_dict_by_keyword(log_lines, log_type):

    for line in log_lines:
        # split words by ': ,'
        splited_line = regex.split(r'[:|,\[\] \(\)<>=]+', line)

        # store log by word to dict recursively
        temp_dict = log_type
        for i in range(len(splited_line)):
            # should not happen
            if splited_line[i] == '':
                splited_line[i] = '!!!!!!!!!!!!!!!!!!'
            if splited_line[i] not in temp_dict.keys():
                temp_dict[splited_line[i]] = {}
            temp_dict = temp_dict[splited_line[i]]
    # log_type = dict(sorted(log_type.items(), key=lambda x: x[0], reverse=True))
    return log_type


def txt_to_log_word_count(log_lines, log_type):

    for line in log_lines:
        # split words by ': ,'
        splited_line = regex.split(r'[:|,\[\] \(\)<>=]+', line)

        # count the appear times of each word
        for i in range(len(splited_line)):
            # should not happen
            if splited_line[i] == '':
                splited_line[i] = '!!!!!!!!!!!!!!!!!!'
            if splited_line[i] not in log_type.keys():
                log_type[splited_line[i]] = 0
            log_type[splited_line[i]] = log_type[splited_line[i]] + 1
    # log_type = dict(sorted(log_type.items(), key=lambda x: x[1], reverse=True))
    return log_type


if __name__ == '__main__':

    input_file_path = '.\\syslog.log'
    output_file_path = '.\\test.txt'
    capture_type = 'kernel'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:t:", [
                                   "input_file_path=", "output_file_path="])
    except getopt.GetoptError:
        print('GetoptError')
        sys.exit(2)

    for i in opts:
        if len(i) != 2:
            print("Something wrong with opts")
            raise getopt.GetoptError
        if i[0] == '-i':
            # example.xlsx:sheet tag
            # sheet tag will be using at separate same sheet name from different file
            # input_file_list.append(i[1].split(':'))
            input_file_path = i[1]
        elif i[0] == '-o':
            output_file_path = i[1]
        elif i[0] == '-t':
            capture_type = i[1]

    # load replace yaml
    remove_yaml_file = open('txt_remove.yaml', 'r', encoding='utf-8')
    remove_yaml = yaml.load(remove_yaml_file, yaml.CFullLoader)
    #replace_yaml_file = open('txt_replace.yaml', 'r', encoding='utf-8')
    #replace_yaml = yaml.load(replace_yaml_file, yaml.CFullLoader)
    #model_list_file = open('model_list.yaml', 'r', encoding='utf-8')
    #model_list = yaml.load(model_list_file, yaml.CFullLoader)

    log_file = open(input_file_path, 'r', encoding='utf-8',
                    errors='ignore')

    log_lines = log_file.readlines()
    log_times, log_lines = split_time_from_log(log_lines)
    log_lines = remove_useless_char(log_lines)
    #log_lines = replace_keywords(log_lines)
    log_lines = combine_time_log(log_times, log_lines)
    log_lines_by_type = log_separate_by_type(log_lines, capture_type)

    f = open('syslog_' + capture_type + '.txt', 'w', encoding='utf-8')
    f.writelines(log_lines_by_type)
    f.close()
