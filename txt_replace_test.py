import os
import re
import yaml
import regex


def remove_control_characters(string):
    return regex.sub(r'\p{C}', '', string)


if __name__ == '__main__':

    # get files list
    logfloder_path = './TracelineLog/'
    log_paths = []

    log_type = {}

    # load replace yaml
    replace_yaml_file = open('txt_replace.yaml', 'r', encoding='utf-8')
    model_list_file = open('model_list.yaml', 'r', encoding='utf-8')
    replace_yaml = yaml.load(replace_yaml_file, yaml.CFullLoader)
    model_list = yaml.load(model_list_file, yaml.CFullLoader)

    # raw_log_by_type
    log_file = open('raw_log_by_type.txt', 'r', encoding='utf-8',
                    errors='ignore')
    log_lines = log_file.readlines()

    for i in range(len(log_lines)):
        # remove control chars
        log_lines[i] = remove_control_characters(log_lines[i])

        # find time in log
        # sometimes it will contain some noise at the front of log
        log_shift = 0
        time_search = re.search(
            '[0-9] ([0-9]{2}:){2}[0-9]{2} ', log_lines[i])
        if time_search != None:
            log_shift = time_search.span()[1]
            log_lines[i] = log_lines[i][log_shift:]
        raw_line = log_lines[i]
        # replace model_name: model should be replace before keywords
        for model in model_list:
            # model names have a lot of variants,
            # so consider #$%#$%(model_name)!@#$@#$ as a model_name
            log_lines[i] = re.sub(
                r'(?i)' + model + '([0-9A-Za-z_-]{0,})', '_MODEL_NAME', log_lines[i])

        # replace keywords
        for rule in replace_yaml:
            log_lines[i] = re.sub(
                replace_yaml[rule]['regex'], replace_yaml[rule]['replace'], log_lines[i])

        if log_lines[i] not in log_type.keys():
            log_type[log_lines[i]] = raw_line
    # write result to file
    log_file_replaced = open('raw_log_by_type_replaced.txt', 'w', encoding='utf-8',
                             errors='ignore')
    for i in range(len(log_lines)):
        log_lines[i] = log_lines[i] + '\n'
    log_file_replaced.writelines(log_lines)
