import sys
import json
import regex
from datetime import datetime
import getopt

remove = {
    'Noise ^[[': {
        'regex': '(\^\[{2}[0-9]{0,2}(\;[0-9]{0,2})*m)',
        'replace': '',
    },
    'Noise %M': {
        'regex': '((?<=[^A-Za-z0-9])|^)((\^M[0-9]+%%)+)((?=[^A-Za-z0-9])|$)',
        'replace': '',
    },
    'Noise ^M': {
        'regex': '\^M',
        'replace': '',
    }
}


def remove_control_characters(string):
    return regex.sub(r'\p{C}', '', string)


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
            try:
                log_times.append(datetime.strptime(
                    year + log_lines[i][log_shift-16:log_shift], r'%Y%b %d %H:%M:%S '))
            except ValueError:
                continue
            log_lines[i] = log_lines[i][log_shift:]
        else:
            log_times.append(None)
    return log_times, log_lines


def remove_useless_char(log_lines):
    for i in range(len(log_lines)):
        # remove control chars
        log_lines[i] = remove_control_characters(log_lines[i])

        # remove matched chars
        for rule in remove:
            log_lines[i] = regex.sub(
                remove[rule]['regex'], remove[rule]['replace'], log_lines[i])

    return log_lines


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

    try:
        log_file = open(input_file_path, 'r', encoding='utf-8',
                        errors='ignore')
    except IOError:
        print('IOError')

    log_lines = log_file.readlines()
    log_times, log_lines = split_time_from_log(log_lines)
    log_lines = remove_useless_char(log_lines)

    program_name_line = -99
    program_name = ''
    result = []

    for i in range(len(log_lines)):
        # for each line
        # match kernel: .... comm: (program_name) ...
        program_name_search = regex.search(
            r'(?i)kernel:.+comm:[\s]+([\S]+)', log_lines[i])
        # match kernel: .... PC is at (0x0000000) ...
        program_counter_search = regex.search(
            r'(?i)kernel:[\s]+PC is at ([x0-9a-f]+)', log_lines[i])

        # record the line found a crashed program
        if program_name_search != None:
            program_name = program_name_search.captures(1)[0]
            print(program_name)
            program_name_line = i

        # if the pc and the found crashed program are within 10 line
        # count as a pair
        if program_counter_search != None:
            print(program_counter_search.captures(1)[0])

        if program_counter_search != None and program_name_line + 10 >= i and program_name != '':
            result.append(
                (program_name, program_counter_search.captures(1)[0]))

    if len(result) != 0:

        try:
            output_file = open(output_file_path, 'w', encoding='utf-8')
        except IOError:
            print('IOError')

        output_file.writelines(json.dumps(
            result, sort_keys=False, skipkeys=False, indent=4))
