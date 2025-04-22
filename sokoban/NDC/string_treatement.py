def parse_input(input_str):
    lines = input_str.splitlines()
    main_string = []
    metadata = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
        else:
            main_string.append(line.strip())
    
    main_string = '\n'.join(main_string).strip()
    
    return main_string, metadata

def format_output(main_string, metadata):
    formatted_string = main_string + '\n'
    
    for key, value in metadata.items():
        formatted_string += f"{key}: {value}\n"
    
    return formatted_string.strip()

string = """
_#####
##---#
#+$--#
######

ID: 3345
Title: Level 1
Collection: Choriban
Author: Marti Homs Caussa
"""

BIG_STRING = open("test.txt", 'r').read().split('\n\n')

from test import append_to_file, treat_string, clear_file
from tqdm import tqdm

clear_file("test_test.txt")
for string in tqdm(BIG_STRING, desc="Progress"):
    treated = treat_string(parse_input(string)[0])
    append_to_file("test_test.txt", treated)


print()