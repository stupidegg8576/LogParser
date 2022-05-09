import regex
import os


def remove_control_characters(string):
    return regex.sub(r'\p{C}', '', string)


def get_variable_name(line: str):
    if type(line) != str:
        raise TypeError('input ' + str(type(line)) + ', input should be str')
    # if there is | in line, use user setting
    if '|' in line:
        splited = regex.split(r'[|]', line)[-1]
        return regex.split(r'[, ]+', splited)

    # if there is no | in line
    elif '(' in line:
        splited = regex.split(r'[ \t]', line)
        variables = []
        for i in range(len(splited)):
            if '(' in splited[i]:
                # try to find if there is a word inside ( )
                if regex.search(r'\(([A-Za-z0-9_-]+)\)', splited[i]) != None:
                    variables.append(regex.search(
                        r'\(([A-Za-z0-9_-]+)\)', splited[i]).group(1))
                # if the string inside ( ) is not a word
                # try the string before ( )
                elif i != 0 and regex.search(r'[A-Za-z0-9_-]+', splited[i-1]):
                    variables.append(regex.search(
                        r'[A-Za-z0-9_-]+', splited[i-1]).group(0))
                else:
                    variables.append(
                        'Something wrong in searching variable name')
        return variables

    # return a empty string
    else:
        return []


if __name__ == '__main__':

    with open('Traceline_driver_stat_parser/format.txt', 'r', encoding='utf-8', errors='ignore') as format_file:
        lines = format_file.readlines()

    command_set = 'Something wrong'
    command_name = 'Something wrong'
    is_command_set = False
    is_command_name = False

    format_dict = {}
    recursive = []
    indent = -1
    for i in len(lines):

        line = remove_control_characters(lines[i])
        # start with ==============
        if regex.match(r'^={10}', line) != None:
            is_command_set = not is_command_set
        # start with ------------------
        elif regex.match(r'^-{10}', line) != None:
            is_command_name = not is_command_name

        else:
            if is_command_set and is_command_name:
                raise BaseException(
                    'Something wrong with finding command_set and command_name')

            elif is_command_set:
                command_set = get_variable_name(line)
                if command_set not in format_dict.keys():
                    format_dict[command_set] = {}
                    format_dict[command_set]['regex'] = line.split('|')[0]

            elif is_command_name:
                command_name = get_variable_name(line)
                if command_name not in format_dict[command_set].keys():
                    format_dict[command_set][command_name] = {}
                    format_dict[command_set][command_name]['regex'] =\
                        line.split('|')[0]
                    format_dict[command_set][command_name]['child'] = {}
            # is
            else:
