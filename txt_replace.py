import os
import re
import yaml


if __name__ == '__main__':

    # get files list
    logfloder_path = './TracelineLog/'
    log_paths = []

    # load replace yaml
    replace_yaml_file = open('txt_replace.yaml', 'r', encoding='utf-8')
    replace_yaml = yaml.load(replace_yaml_file, yaml.CFullLoader)

    # TracelineLog \ model_name \ report_ID
    for model_name in os.listdir(logfloder_path):
        for report_ID in os.listdir(logfloder_path + model_name):
            if os.path.exists(logfloder_path + model_name + '/' + report_ID + '/syslog.log'):
                log_paths.append(logfloder_path + model_name +
                                 '/' + report_ID)

    for log_path in log_paths:
        print(log_path)
        log_file = open(log_path + '/syslog.log', 'r', encoding='utf-8',
                        errors='ignore')
        log_lines = log_file.readlines()

        for i in range(len(log_lines)):
            for rule in replace_yaml:
                log_lines[i] = re.sub(
                    replace_yaml[rule]['regex'], replace_yaml[rule]['replace'], log_lines[i])

        log_file_replaced = open(log_path + '/syslog_replaced.log', 'w', encoding='utf-8',
                                 errors='ignore')
        log_file_replaced.writelines(log_lines)
