import sys
import os
import datetime

logfloder_path = './TracelineLog/'
logfiles = []

for model_name in os.listdir(logfloder_path):
    for report_ID in os.listdir(logfloder_path + model_name):
        if os.path.exists(logfloder_path + model_name + '/' + report_ID + '/syslog.log'):
            logfiles.append(logfloder_path + model_name +
                            '/' + report_ID + '/syslog.log')

log_type = {}

for log_path in logfiles:

    log = open(log_path, 'r', encoding='utf-8', errors='ignore').readlines()
    for line in log:
        t = line[16:].split(':')[0]
        if '[' in t:
            t = t.split('[')[0]
        if t == '':
            print(line)
        if t not in log_type:
            log_type[t] = 0
        log_type[t] = log_type[t] + 1

log_type = sorted(log_type.items(), key=lambda x: x[1])

print(log_type)
