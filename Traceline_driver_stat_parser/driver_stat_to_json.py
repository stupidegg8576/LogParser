import regex
import os
import json
import getopt
import sys


def remove_control_characters_lines(lines):
    for i in range(len(lines)):
        lines[i] = remove_control_characters(lines[i])
    return lines


def remove_control_characters(string):
    return regex.sub(r'\p{C}', '', string)


def find_command(command: str, format_lines):
    is_command = False
    command_start = -1
    command_end = len(format_lines) - 1
    for i in range(len(format_lines)):
        if regex.match(r'^-{10}', format_lines[i]) != None:
            is_command = not is_command
        elif is_command:
            if regex.search(format_lines[i], command) != None:
                command_start = i
                break
    for i in range(command_start + 2, len(format_lines)):
        if regex.match(r'^[=-]{10}', format_lines[i]) != None:
            command_end = i - 1
            break
    return command_start, command_end


def find_command_set(command_set, format_lines):
    is_command_set = False
    command_set_start = -1
    command_set_end = len(format_lines) - 1
    for i in range(len(format_lines)):
        if regex.match(r'^={10}', format_lines[i]) != None:
            is_command_set = not is_command_set
        elif is_command_set:
            if regex.search(format_lines[i], command_set) != None:
                command_set_start = i
                break
    for i in range(command_set_start + 2, len(format_lines)):
        if regex.match(r'^[=]{10}', format_lines[i]) != None:
            command_set_end = i - 1
            break
    return command_set_start, command_set_end


def get_variable_name(line: str):
    if type(line) != str:
        raise TypeError('input ' + str(type(line)) + ', input should be str')
    # if there is | in line, use user setting
    if '|' in line:
        splited = regex.split(r'[|]', line)[-1]
        splited = regex.sub('\s', '', splited)
        return regex.split(r',', splited)

    # if there is no | in line
    elif '(' in line:
        line = regex.sub(r'[ \t]', '', line)
        splited = regex.split(r'([\(\)])', line)
        variables = []
        # find word in ( )
        for i in range(len(splited)):
            if i + 2 < len(splited):
                if splited[i] == '(' and splited[i+2] == ')':
                    if regex.match(r'[A-Za-z0-9]', splited[i+1]) != None:
                        variables.append(splited[i+1])
        # if can't find a word, try the first split not empty
        if len(variables) == 0:
            for i in range(len(splited)):
                if splited[i] != '':
                    variables.append(splited[i+1])
                    break
        # if still can't find anything
        if len(variables) == 0:
            variables.append('Something wrong in searching variable name')

        return variables

    # return a empty string
    else:
        return ['Something wrong in searching variable name']


if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:f:", [
                                   "input_file_path=", "output_file_path=", "format.txt="])
    except getopt.GetoptError:
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
        elif i[0] == '-f':
            format_file_path = i[1]

    input_file_path = 'Traceline_driver_stat_parser/WlGetDriverStats_eth4.log'
    output_file_path = 'Traceline_driver_stat_parser/test.json'
    format_file_path = 'Traceline_driver_stat_parser/format.txt'

    with open(format_file_path, 'r', encoding='utf-8', errors='ignore') as format_file:
        format_lines = remove_control_characters_lines(format_file.readlines())
    with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as log_file:
        log_lines = remove_control_characters_lines(log_file.readlines())
    command_set = 'Something wrong'
    command_name = 'Something wrong'
    is_command_set = False
    is_command = False

    result = {}
    last_matched = -1
    for log_count in range(len(log_lines)):

        # start with ==============
        if regex.match(r'^={10}', log_lines[log_count]) != None:
            is_command_set = not is_command_set
        # start with ------------------
        elif regex.match(r'^-{10}', log_lines[log_count]) != None:
            is_command = not is_command

        else:
            if is_command_set and is_command:
                raise BaseException(
                    'Something wrong with finding command_set and command_name')

            elif is_command_set:
                command_set_start, command_set_end = find_command_set(
                    log_lines[log_count], format_lines)
                if command_set_start != -1:
                    command_set = get_variable_name(
                        format_lines[command_set_start])[0]
                    for n in range(0, 10):
                        # may test more than one times
                        if (command_set + '_' + str(n)) not in result.keys():
                            command_set = command_set + '_' + str(n)
                            result[command_set] = {}
                            break
                        # if already in it, goto next number
                        else:
                            continue
                # skip command set that can't recognized
                else:
                    command_set = 'No matched'
                    pass
                    #raise BaseException("Found no matched command set")

            elif is_command:
                last_matched, format_end = find_command(
                    log_lines[log_count], format_lines)
                if last_matched != -1:
                    command_name = get_variable_name(
                        format_lines[last_matched])[0]
                    if command_name not in result[command_set].keys():
                        result[command_set][command_name] = {}
                # skip command that can't recognized
                else:
                    command_name = 'No matched'
                    pass
                    #raise BaseException("Found no matched command")
            # is normal log line
            # find a matched format line
            # and store value to result[command_set][command_name]
            else:
                # not a recognized command, or a wrong format
                # skip
                if last_matched == -1:
                    continue

                match = regex.match(
                    format_lines[last_matched], log_lines[log_count])
                # if not matched, move to next format line
                temp = last_matched
                while match == None:
                    temp = temp + 1
                    if temp > format_end:
                        temp = -1
                        break
                    match = regex.match(
                        format_lines[temp], log_lines[log_count])
                # can't find matched log format
                # skip this log line
                if match == None:
                    log_count = log_count + 1
                    continue
                else:
                    last_matched = temp

                variable_name = get_variable_name(format_lines[last_matched])
                # skip group(0)
                for i in range(1, len(match)):
                    result[command_set][command_name][variable_name[i-1]
                                                      ] = match.group(i)

    for command_set in result:
        print(command_set)
        for command in result[command_set]:
            print('\t' + command)
            for var in result[command_set][command]:
                print('\t\t' + var + ' : ' +
                      result[command_set][command][var])
    with open(output_file_path, 'w', encoding='utf-8', errors='ignore') as output_file:
        output_file.write(json.dumps(result, skipkeys=True))
