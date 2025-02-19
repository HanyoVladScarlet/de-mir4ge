import os
import sys


ROOT_PATH = 'C:/Users/hanyo/Documents/Hatuki/Github/de-mirage/src/fragmentor/assets/models'


def clean_up_blend1s(root_path = ROOT_PATH):
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        root_path = ROOT_PATH
    for r, d, f in os.walk(root_path):
        for file in f:
            if not file.endswith('.blend1'):
                continue
            os.remove(os.path.join(r, file))


if __name__ == '__main__':
    clean_up_blend1s()