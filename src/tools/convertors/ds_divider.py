import os
import multiprocessing
import shutil
import time


'''
Use this module to divide the dataset into `train_set` / `val_set` / `test_set`
'''

P_FROM = r'C:\Users\hanyo\Desktop\yolo-data'
P_TO = r'C:\Users\hanyo\Desktop\yolo-data\yolo-data'
PARTITION = [8, 2, 1]

def main():
    d = DataCarrier(P_FROM, P_TO, PARTITION)
    d.execute()

class DataCarrier():
    def __init__(self, p_from, p_to, partition):
        self._t_start = time.time()
        self._p_from_image = os.path.join(p_from, 'images')
        self._p_from_label = os.path.join(p_from, 'labels')
        self._p_to_train_image = os.path.join(p_to, 'train', 'images')
        self._p_to_train_label = os.path.join(p_to, 'train', 'labels')
        self._p_to_val_image = os.path.join(p_to, 'val', 'images')
        self._p_to_val_label = os.path.join(p_to, 'val', 'labels')
        self._p_to_test_image = os.path.join(p_to, 'test', 'images')
        self._p_to_test_label = os.path.join(p_to, 'test', 'labels')
        self._p_images = [f for f in os.listdir(self._p_from_image)]
        self._p_labels = [f for f in os.listdir(self._p_from_label)]
        # self._p_images = [f for f in os.listdir(self._p_from_image) if os.path.isfile(f) and f.lower().endswith('.png')]
        # self._p_labels = [f for f in os.listdir(self._p_from_label) if os.path.isfile(f) and f.lower().endswith('.txt')]
        print(self._p_images)
        if not os.path.exists(self._p_to_train_image):
            os.makedirs(self._p_to_train_image)
        if not os.path.exists(self._p_to_train_label):
            os.makedirs(self._p_to_train_label)
        if not os.path.exists(self._p_to_val_image):
            os.makedirs(self._p_to_val_image)
        if not os.path.exists(self._p_to_val_label):
            os.makedirs(self._p_to_val_label)
        if not os.path.exists(self._p_to_test_image):
            os.makedirs(self._p_to_test_image)
        if not os.path.exists(self._p_to_test_label):
            os.makedirs(self._p_to_test_label)
        self._count_upper_test = len(self._p_images)
        self._count_upper_val = int(self._count_upper_test * (1 - partition[-1] / sum(partition)))
        self._count_upper_train = int(self._count_upper_test * partition[0] / sum(partition))

    
    def execute(self):
        core_count = multiprocessing.cpu_count()
        for count in range(0, self._count_upper_test, core_count):
            try:
                pool = multiprocessing.Pool()
                pool.map(self.carry_one, [i for i in range(count, count + core_count)])
                pool.close()
                pool.join()
            except Exception as e:
                print(e)

    def carry_one(self, idx):
        t_start = time.time()
        # 处理images
        p_from = os.path.join(self._p_from_image, self._p_images[idx])
        if idx < self._count_upper_train:
            p_to_folder = self._p_to_train_image
        elif idx < self._count_upper_val:
            p_to_folder = self._p_to_val_image
        else:
            p_to_folder = self._p_to_test_image
        p_to = os.path.join(p_to_folder, self._p_images[idx])
        shutil.copy(p_from, p_to)
        # 处理labels
        p_from = os.path.join(self._p_from_label, self._p_labels[idx])
        if idx < self._count_upper_train:
            p_to_folder = self._p_to_train_label
        elif idx < self._count_upper_val:
            p_to_folder = self._p_to_val_label
        else:
            p_to_folder = self._p_to_test_label
        p_to = os.path.join(p_to_folder, self._p_labels[idx])
        shutil.copy(p_from, p_to)
        t_now = time.time()
        print(f'{idx + 1} of {self._count_upper_test} item accomplish carrying in {t_start - t_now}.')
        print(f'Sum up to {(t_now - self._t_start)} seconds have elapsed.\n')

if __name__ == '__main__':
    main()