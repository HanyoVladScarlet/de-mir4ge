import os
import sys
import json
import time
import cv2
import random
import signal
import multiprocessing


DEFAULT_INPUT_FOLDER = r'C:\Users\hanyo\Desktop\outputs\output_2025-02-13-23-51-39'
DEFAULT_OUTPUT_FOLDER = r'C:\Users\hanyo\Desktop\outputs\foregrounds'
LOG_NAME = 'labels'
ALPHA_CUTOFF = True
OPAQUE_THRESHOLD = 32
BLACK_LIST = ['src/fragmentor/assets/models/car/Mercedes_Benz_Actros_2015.blend', 'src/fragmentor/assets/models/car/Mercedes-Benz_300_(W108)_SEL_AMG_Red_Pig_1969.blend', 'src/fragmentor/assets/models/car/Mercedes-Benz_CapaCity_L_4door_Bus_HQinterior_2014.blend', 'src/fragmentor/assets/models/car/Toyota Yaris Hatchback US 2020.blend']

def main():
    alpha_cutoff = ALPHA_CUTOFF
    input_path = DEFAULT_INPUT_FOLDER
    blacklist_ = BLACK_LIST
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f'Path {input_path} does not exist!')
        return
    output_path = DEFAULT_OUTPUT_FOLDER
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for i in sys.argv:
        if i == '-a':
            alpha_cutoff = True
    cvt = Convertor(input_path, output_path, alpha_cutoff, blacklist_)
    cvt.convert()
    print('hao')


class Convertor():
    def __init__(self, source, destination, alpha_off, blacklist_):
        self._t_start = time.time()
        self._source = source
        self._destination = destination
        self._alpha_cutoff = alpha_off
        self._blacklist_ = blacklist_
        self._log_files = []
        for r, d, f in os.walk(self._source):
            for file in f:
                # print(r, file)
                if file.endswith('.json'):
                    self._log_files.append(os.path.join(r, file).replace('\\', '/'))
        self._total = len(self._log_files)




    def convert(self):
        core_count = multiprocessing.cpu_count()
        for count in range(0, self._total, core_count):
            try:
                pool = multiprocessing.Pool()
                pool.map(self.convert_one, [i for i in range(count, count + core_count)])
                pool.close()
                pool.join()
            except Exception as e:
                print(e)
        return


    def convert_one(self, idx):
        res = None
        with open(self._log_files[idx], 'r') as f:
            s_json = f.read()
        o_json = json.loads(s_json)
        model_path = o_json['model-path']
        if model_path is None:
            return
        # shutil.copy2
        # print(f'{idx} of {total} has been output at `{output_path}`.')
        # print(f'{idx} of {total} has been output at `{log_path}`.')
        s_image = os.path.join(self._source, 'images', o_json['name'] + '.png')
        d_image = os.path.join(self._destination, 'images', o_json['cls'])
        if not os.path.exists(d_image):
            os.makedirs(d_image)
        d_image = os.path.join(d_image, o_json['name'] + '.png')
        o_cnt = self.image_copy(s_image, d_image, self._alpha_cutoff)
        res = json.dumps({
            'cls': o_json['cls'],
            'cam-rot-x':  o_json['sun_rot_x'],
            'cam-rot-z':  o_json['sun_rot_z'],
            'model-path': o_json['model-path'], 
            'name': o_json['name'],
            'o-cnt': o_cnt,
        })
        output_path = os.path.join(self._destination, LOG_NAME, o_json['cls'])
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_path = os.path.join(output_path, o_json['name'] + '.json')
        with open(output_path, 'w+') as f:
            f.write(res)
        time.sleep(random.random() * 0.8 + 0.2)
        print(f'{idx} of {self._total} images have been accomplished within {time.time() - self._t_start} seconds.\n')
        return


    def image_copy(self, source, destination, alpha_cutoff):
        opaque_count = 0
        try:
            output = cv2.imread(source, cv2.IMREAD_UNCHANGED)
            if output is None:
                print(f'File {source} is not an image.')    
                return
            if len(output.shape) < 3:
                print(f'Image {source} is less than 3 channels.')
                return
            if output.shape[2] < 4:
                print(f'Image {source} has no alpha channel.')
                return
            if alpha_cutoff:
                x_max = -1
                y_max = -1
                x_min = output.shape[0]
                y_min = output.shape[1]    
                flag_x = True
                # print(output is None)
                for i in range(output.shape[0]):
                    for j in range(output.shape[1]):
                        if output[i][j][3] > 0:
                            opaque_count += 1
                            if flag_x:
                                x_min = i
                                flag_x = False
                            x_max = max(x_max, i)
                            y_max = max(y_max, j)
                            y_min = min(y_min, j)
                if opaque_count < OPAQUE_THRESHOLD:
                    return
                output = output[x_min:x_max+1, y_min:y_max+1]
            cv2.imwrite(destination, output, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            if alpha_cutoff:
                print(f'Image `{source}` has been alpha cut-off to `    {destination}`.')  
                return opaque_count
            print(f'Image `{source}` has been copied to `{destination}`.')  

        except Exception as e:
            print(e)
        return 


if __name__ == '__main__':
    main()
