import regex
from datetime import datetime
import getopt
import json
import sys


class mem():
    def __init__(self, pid, date, size) -> None:
        self.pid = pid
        self.date = datetime.strptime(
            date, r'%a %b %d %H:%M:%S %Y')
        self.size = size


def read_psstate_file(input_path):
    with open(input_path) as input_file:
        input_data = input_file.readlines()
    return input_data


def get_mem_usage_from_txt(input_txt_data):

    mem_usage = {}
    func = 'Something wrong'

    for line in input_txt_data:

        # check if line is a new func
        match_pid = regex.match(
            r'[\s]+([\S]+)[\s]+pid[\s]+subname[\s]+timestamp[\s]+vsz\(kb\)[\s]+state', line)

        if match_pid != None:
            func = match_pid.group(1)
            if func not in mem_usage.keys():
                mem_usage[func] = {}
            continue

        # check if line is a mem usage record
        # pid =         group(1)
        # time =        group(2)
        # mem_usage =   group(3)
        match_mem = regex.match(
            r'[\s]+\[[\s]*([\0-9]+)\][\s]+[\S]+[\s]+([\S]+ +[\S]+ +[\S]+ [\S]+ +[\S]+)[\s]+([0-9]+)[\s]+[\S]+[\s]*', line)

        if match_mem != None:

            pid = int(match_mem.group(1))
            date = match_mem.group(2)
            mem_size = int(match_mem.group(3))

            if pid not in mem_usage[func].keys():
                mem_usage[func][pid] = []

            temp = mem(pid, date, mem_size)

            if temp.date.year != 2018:
                mem_usage[func][pid].append(temp)

    return mem_usage


def parse_mem_usage(mem_usage):
    bad_funcs = {}
    for func in mem_usage:
        for pid in mem_usage[func]:
            previous_mem = None
            rising = 0
            for i in range(len(mem_usage[func][pid])):
                now_mem = mem_usage[func][pid][i]
                if previous_mem == None:
                    pass
                elif now_mem.size > previous_mem.size:
                    rising = rising + 1
                else:
                    rising = 0

                # mem usage keep risng
                if rising >= 2:

                    func = func
                    if func not in bad_funcs.keys():
                        bad_funcs[func] = {}
                    if pid not in bad_funcs[func].keys():
                        bad_funcs[func][pid] = {}
                    bad_funcs[func][pid]['start_time'] = mem_usage[func][pid][0].date.strftime(
                        '%Y-%b-%d %H:%M:%S')
                    bad_funcs[func][pid]['end_time'] = mem_usage[func][pid][-1].date.strftime(
                        '%Y-%b-%d %H:%M:%S')
                    if mem_usage[func][pid][-1].size != 0:
                        end_size = mem_usage[func][pid][-1].size
                    else:
                        end_size = mem_usage[func][pid][-2].size
                    bad_funcs[func][pid]['start_size'] = mem_usage[func][pid][0].size
                    bad_funcs[func][pid]['end_size'] = end_size
                    bad_funcs[func][pid]['increased rate'] = format(
                        end_size / mem_usage[func][pid][0].size, '.2f')

                previous_mem = mem_usage[func][pid][i]
    return bad_funcs


if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:", [
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

    input_txt_data = read_psstate_file(
        input_file_path)

    mem_usage = get_mem_usage_from_txt(input_txt_data)

    with open(output_file_path, 'w', encoding='utf-8', errors='ignores') as output_file:
        output_file.writelines(json.dumps(parse_mem_usage(mem_usage)))
