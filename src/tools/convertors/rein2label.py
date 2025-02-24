import json
import multiprocessing
import os
import shutil
import time
import yaml

from datetime import datetime as dt


P_FROM = r'C:\Users\hanyo\Documents\Hatuki\Github\de-mirage\src\reincarnator\outputs\output_2025-02-22-00-04-10'
P_TO = r'C:\Users\hanyo\Desktop\yolo-data'
NAME = 'yolo-data'

def main():
    ''''''
    d = DataStructor(P_FROM, P_TO, NAME)
    d.to_yolo()



class DataStructor():
    def __init__(self, p_from, p_to, name):
        self._t_start = time.time()
        self._logs = []
        self._p_log = os.path.join(p_to, 'logs')
        self._f_labels = []
        self._config = {}
        with open(os.path.join(p_from, 'config.json'), 'r') as f:
            self._config = json.loads(f.read())
        self._t_width = self._config['params']['target_width']
        self._t_height = self._config['params']['target_height']
        l_cls = list(self._config['paths']['foreground'].keys())
        self._cls_dict = {}
        for i in range(len(l_cls)):
           self._cls_dict[l_cls[i]] = i 
        self._p_labels = os.path.join(p_to, 'labels')
        self._p_images = os.path.join(p_to, 'images')
        self._p_from_images = os.path.join(p_from, 'images')
        self._p_cls_info = os.path.join(p_to, name + '.yml')
        if not os.path.exists(self._p_images):
            os.makedirs(self._p_images)
        if not os.path.exists(self._p_labels):
            os.makedirs(self._p_labels)
        if not os.path.exists(self._p_log):
            os.makedirs(self._p_log)
        for r, d, f in os.walk(os.path.join(p_from, 'labels')):
            for file in f:
                item = os.path.join(r, file)
                self._f_labels.append(item)
        self._output_count = len(self._f_labels)

    def to_yolo(self, mul_proc=True):
        with open(self._p_cls_info, 'w+') as f:
            s_yml = yaml.dump({
                'nc': len(self._cls_dict.keys()),
                'names': list(self._cls_dict.keys()),
                'train': '',
                'val': '',
                'test': '',
            })
            f.write(s_yml)
        if not mul_proc:
            for i in range(len(self._f_labels)):
                self.get_one_yolo(i)
            return
        core_count = multiprocessing.cpu_count()
        for count in range(0, self._output_count, core_count):
            try:
                pool = multiprocessing.Pool()
                pool.map(self.get_one_yolo, [i for i in range(count, count + core_count)])
                pool.close()
                pool.join()
            except Exception as e:
                print(e)
                self.write_log(e)
        return
            
    
    def get_one_yolo(self, idx):
        t_start = time.time()
        f_label = self._f_labels[idx]
        label = self.parse_one(f_label)
        if label is None:
            return
        labels = []
        for ins in label['ins_arr']:
            ins_width = (ins['x_max'] - ins['x_min']) / self._t_width
            ins_height = (ins['y_max'] - ins['y_min']) / self._t_height
            ins_pos_x = (ins['x_max'] + ins['x_min']) / 2 / self._t_width
            ins_pos_y = (ins['y_max'] + ins['y_min']) / 2 / self._t_height
            ins_cls = self._cls_dict[ins['cls']]
            labels.append(f'{ins_cls} {ins_pos_x} {ins_pos_y} {ins_width} {ins_height}')
        self.write_one_label(label['name'], '\n'.join(labels), '.txt')
        print(f'{idx + 1} of {self._output_count} images accomplish labeling with stretch {time.time() - t_start}.')
        print(f'Sum up to {(time.time() - self._t_start)} seconds have elapsed.\n')


    def write_one_label(self, name, content, ext):
        if not ext.startswith('.'):
            ext = '.' + ext
        p_label = os.path.join(self._p_labels, name + ext)
        with open(p_label, 'w') as f:
            f.write(content)
        return 

    def parse_one(self, p_label):
        with open(p_label, 'r') as f:
            res = json.loads(f.read())
        p_image = os.path.join(self._p_images, res['name'] + '.png')
        p_from_image = os.path.join(self._p_from_images, res['name'] + '.png')     
        if not os.path.exists(p_from_image):
            return
        shutil.copy(p_from_image, p_image)
        return res 

    def write_log(self, content):
        content = f'[{dt.now().strftime("%Y-%m-%d-%H-%M-%S")}] {content}'
        self._logs.append(content)
        return
    
    def save_log(self):
        name = dt.now().strftime('%Y-%m-%d-%H-%M-%S')
        p_log = os.path.join(self._p_log, name + '.log')
        with open(p_log, 'w+') as f:
            f.write('\n'.join(self._logs))
        return
    
if __name__ == '__main__':
    main()