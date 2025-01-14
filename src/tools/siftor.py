# encoding=utf-8
# author=Lyapunov


import os
import cv2
import time
import shutil


'''
Use this module to sift out qualified images.
'''

def sift(folder, output_path='/sift-result/', filters=[]):
    files = fetch(folder, filters)
    for file in files:
        dst = os.path.join(output_path, os.path.abspath(file).split(os.path.abspath(folder))) 
        shutil.copyfile(file, dst)


def fetch(folder, filters=[]):
    t_start = time.time()
    if not os.path.exists(folder):
        return 0

    if '.png' not in filters:
        filters.append('.png')
    if '.jpg' not in filters:
        filters.append('.jpg')
    if '.bmp' not in filters:
        filters.append('.bmp')

    paths = []

    for root, _, files in os.walk(folder):
        for file in files:
            if len(filters) > 0:
                flag = False
                for filter in filters:
                    if filter in file:
                        flag = True
                        break
                if not flag:
                    continue
            paths.append(os.path.join(root, file))
    
