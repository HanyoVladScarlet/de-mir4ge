from utils.grinder import Grinder
from utils.logger import info
from datetime import datetime as dt
from utils.file_writer import FileWriter
import json
import time

FOREGROUND_ROOT = 'C:/Users/hanyo/Documents/Hatuki/Github/de-mirage/src/fragmentor/outputs/output_08-01-2025-08-06-55'
BACKGROUND_ROOT = 'C:/Users/hanyo/Documents/Hatuki/Github/de-mirage/src/reincarnator/assets/set_0'
OUTPUT_ROOT = 'C:/Users/hanyo/Documents/Hatuki/Github/de-mirage/src/reincarnator/outputs/'


def main():
    name = dt.now().strftime('output_%Y-%m-%d-%H-%M-%S')
    g = Grinder(name)
    fw = FileWriter(name)
    res = []
    start = dt.now()
    count = 100
    for i in range(5):
        item = g.grind_one()
        res.append(item)
        info(f'{i + 1} of {count} images accomplish grinding.')
        info(f'Sum up to {(dt.now()-start).seconds} elapsed.')
    info(res)
    labels = json.dumps({'labels': res})
    fw.write_label(labels)


if __name__ == '__main__':
    main()
    # t_start = dt.now()
    # time.sleep(1)
    # t_end = dt.now()
    # print((t_end - t_start).microseconds / (t_end - t_start).seconds)