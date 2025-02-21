import os
import json


P_SOURCE = r'C:\Users\hanyo\Desktop\cache\output_2025-02-19-17-54-18\logs'
FILES = [
    'item_2025-02-19-18-02-51',
    'item_2025-02-19-18-01-15',
    'item_2025-02-19-18-02-15',
    'item_2025-02-19-18-18-45',
    'item_2025-02-19-18-42-27'
]


def main():
    res = get_black_list(P_SOURCE, FILES)
    print(res)


def get_black_list(p_source, files):
    res = set()
    for file in files:
        p_json = os.path.join(p_source, file + '.json')
        with open(p_json)as f:
            item = json.load(f)
        blend_path = item['model-path']
        if not blend_path is None:
            res.add(blend_path)
    return list(res)

if __name__ == '__main__':
    main()