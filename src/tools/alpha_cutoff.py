# encoding=utf-8
# author=Lyapunov


import os
import cv2
import time


'''
Automatically cut off the transparent pixels outsides the bounding box.
These shall cut off the time and space consumption for loading images.
'''

def alpha_cutoff(folder, filters=[]):
    t_start = time.time()
    if not os.path.exists(folder):
        return 0

    if '.png' not in filters:
        filters.append('.png')
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
    
    idx = 0
    max_cnt = len(paths)
    for path in paths:
        try:
            output = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if output is None:
                print(f'File {path} is not an image.')    
                continue
            if len(output.shape) < 3:
                print(f'Image {path} is less than 3 channels.')
                continue
            if output.shape[2] < 4:
                print(f'Image {path} has no alpha channel.')
                continue
            x_max = -1
            y_max = -1
            x_min = output.shape[0]
            y_min = output.shape[1]    
            flag_x = True
            # print(output is None)
            for i in range(output.shape[0]):
                for j in range(output.shape[1]):
                    if output[i][j][3] > 0:
                        if flag_x:
                            x_min = i
                            flag_x = False
                        x_max = max(x_max, i)
                        y_max = max(y_max, j)
                        y_min = min(y_min, j)
            output = output[x_min:x_max+1, y_min:y_max+1]
            cv2.imwrite(path, output)
            print(f'Image {path} has been alpha cut off.\n{idx} of {max_cnt} images have been accomplished within {time.time() - t_start} seconds.\n')

        except Exception as e:
            max_cnt -= 1
            print(e)
        print(f'All task accomplished, with {idx} of {max_cnt} valid images alpha cut off.\nSum up to {time.time() - t_start} seconds elapsed.')
