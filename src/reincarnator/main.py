from utils.grinder import Grinder
from utils.logger import info
from datetime import datetime as dt
from utils.file_writer import FileWriter
import json
import time


def main():
    name = dt.now().strftime('output_%Y-%m-%d-%H-%M-%S')
    g = Grinder(name)
    fw = FileWriter(name)
    res = []
    start = dt.now()
    count = 10000
    interval = 5
    pointer = 0
    for i in range(count):
        item = g.grind_one()
        res.append(item)
        info(f'{i + 1} of {count} images accomplish grinding.')
        info(f'Sum up to {(dt.now()-start).seconds} seconds have elapsed.')
        pointer += 1
        if pointer > interval:
            labels = json.dumps({'labels': res})
            res = []
            prefix = fw.write_label(labels)
            info(f'Label `{prefix}` has been output.')
            fw.initialize()
            pointer -= interval




if __name__ == '__main__':
    main()
    # t_start = dt.now()
    # time.sleep(1)
    # t_end = dt.now()
    # print((t_end - t_start).microseconds / (t_end - t_start).seconds)