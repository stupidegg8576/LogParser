import yaml
import regex


def convert_type_to_pattern(type_dict, pattern):
    pattern_dict = {}
    for t in type_dict:
        if t[0] == '_':
            pattern_dict['_type'] = 'regex'


if __name__ == 'main__':

    log_type_file = open('log_type.yaml', 'r', encoding='utf-8')
    log_type = yaml.load(log_type_file, yaml.CFullLoader)
    replace_yaml_file = open('txt_replace.yaml', 'r', encoding='utf-8')
    replace_yaml = yaml.load(replace_yaml_file, yaml.CFullLoader)

    log_pattern =
