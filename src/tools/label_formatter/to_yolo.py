import os
import sys
import json


DEFAULT_INPUT_FOLDER = 'C:\Users\hanyo\Documents\Hatuki\Github\de-mirage\src\reincarnator\outputs\output_2025-01-22-10-35-33'
DEFAULT_OUTPUT_FOLDER = ''

def main():
    input_path = DEFAULT_INPUT_FOLDER
    if len(sys.argv) > 0:
        input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f'Path {input_path} does not exist!')
        return
    output_path = DEFAULT_OUTPUT_FOLDER
    if len(sys.argv) > 1:
        output_path = sys.argv[2]
    if os.path.exists(output_path):
        os.makedirs(output_path)