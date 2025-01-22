import cv2
import os
import numpy as np
import random
import hashlib
import time
from datetime import datetime as dt


from utils.singleton import Singleton
from utils.logger import info, log
from utils.config_loarder import ConfigLoader


@Singleton
class Grinder():
    ''''''
    def __init__(self, name, output_ext='png'):
        self._cfl = ConfigLoader()
        background_root = self._cfl.get('paths/background')
        foreground_roots = self._cfl.get('paths/foreground')
        self.output_path = os.path.join(self._cfl.get('paths/output'), name, 'images')
        self._output_ext = output_ext
        self._boundary_threshold = self._cfl.get('params/boundary-threshold')
        self._occlusion_threshold = self._cfl.get('params/occlusion-threshold')
        self._background_imgs = []
        self._foreground_imgs = {}
        for root, _, files in os.walk(background_root):
            for file in files:
                if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.tif'):
                    self._background_imgs.append(os.path.join(root, file))
        for key in foreground_roots.keys():
            t_paths = []
            for root, _, files in os.walk(foreground_roots[key]):
                for file in files:
                    if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.tif'): 
                        t_paths.append(os.path.join(root, file))
            self._foreground_imgs[key] = t_paths
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    
    def grind_one(self, check_zero_instance=True, check_foreground=True):
        '''
        + 在输出之前维持一个三通道的instance_mask, 其中R为实例1的编号, G为实例2的编号, B为混合比例
        + 在输出时维持一个列表, 用于更新对应实例的,用于计算检测框的信息
        '''
        t_start = time.time()
        name = hashlib.md5(dt.now().strftime('%Y-%m-%d %H:%M%S').encode('utf-8')).hexdigest()

        # 随机读取一张背景图像.
        background_img_name = self.get_one_background()
        background_img = cv2.imread(background_img_name, cv2.IMREAD_UNCHANGED)
        if len(background_img.shape) < 3:
            background_img = cv2.cvtColor(background_img, cv2.COLOR_GRAY2BGR)
        if background_img.shape[2] == 3:
            alpha = np.ones(shape=(background_img.shape[0], background_img.shape[1], 1), dtype=np.uint8) * 255
            background_img = np.concatenate((background_img, alpha), axis=2)

        # 初始化实例mask.
        output = background_img.copy()
        instance_mask = np.zeros(shape=output.shape, dtype=np.uint8)
        instance_mask[:, :, 3] = np.ones((instance_mask.shape[0], instance_mask.shape[1])) * 255

        # 于是, 实例数不能超过254
        instance_count = random.randint(1, 5)
        instance_infos = []

        
        for ins_idx in range(1, instance_count+1):

            o_cnt = 0
            f_name = None
            input = None
            key = None
            while o_cnt == 0:
                key = self.get_one_foreground_key()
                f_name = self.get_one_foreground(key)
                input = cv2.imread(f_name, cv2.IMREAD_UNCHANGED)
                o_cnt = self.get_pixel_count(input)
                # 在确认前景不存在零像素的情况下，在第一次循环结束时直接退出.
                if not check_foreground:
                    break
            
            # 初始化该实例的信息.
            instance_info = {
                'f_name': f_name,
                'class': key,
                'x_min': float('inf'),
                'y_min': float('inf'),
                'x_max': float('-inf'),
                'y_max': float('-inf'),
                'p_cnt': 0, 
            }

            # 实例的大小不能过小, 这里认为32是基础值.
            min_scale_ratio = max(float(self._boundary_threshold) / input.shape[0], float(self._boundary_threshold) / input.shape[1])
            max_scale_ratio = min(output.shape[0] / input.shape[0], output.shape[1] / input.shape[1]) 
            scale_ratio = random.random() * (max_scale_ratio - min_scale_ratio) + min_scale_ratio

            input = self.alpha_cutoff(input, ratio=scale_ratio)
            instance_info['o_cnt'] = self.get_pixel_count(input)
            
            x_min = self._boundary_threshold - input.shape[0]
            x_max = output.shape[0] - self._boundary_threshold
            y_min = self._boundary_threshold - input.shape[1]
            y_max = output.shape[1] - self._boundary_threshold
            
            # 使用高斯分布散布实例
            x_offset = int(random.gauss(0.5 * (x_min + x_max), 0.15 * (x_max - x_min)))
            y_offset = int(random.gauss(0.5 * (y_min + y_max), 0.15 * (y_max - y_min)))
            instance_mask = self.get_mask(input, instance_mask, x_offset, y_offset, ins_idx)
            output = self.instance_fit_in(input, output, x_offset, y_offset)
            instance_infos.append(instance_info)


        # Background blending in.
        # 在背景中采样, 并融合进前景当中.
        blending_map = np.ones(background_img.shape) * 255
        output = self.get_pseudo_mask(background_img, output, blending_map)

        # 通过instance_mask来更新instance_info.
        instance_infos = self.get_labels(instance_mask, instance_infos)

        # 检查label中是否存在严重遮挡者.
        for instance_info in instance_infos:
            instance_info['occlusion_rate'] = 1 - instance_info['p_cnt'] / instance_info['o_cnt']
            instance_info['is_valid'] = instance_info['occlusion_rate'] < self._occlusion_threshold
            if not instance_info['is_valid']:
                log(f'Instance {ins_idx} has been occluded.')

        # 防止输出0实例的图像.
        if not check_zero_instance or not all([not label['is_valid'] for label in instance_infos]):
            image_path = os.path.join(self.output_path, f'{name}.png')
            mask_path = os.path.join(self.output_path, f'{name}-masked.png')
            print(image_path)
            cv2.imwrite(image_path, output, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            cv2.imwrite(mask_path, instance_mask, [cv2.IMWRITE_PNG_COMPRESSION, 0])

            return {
                'name': name,
                'time': time.time() - t_start,
                'b_name': background_img_name,
                'labels': instance_infos,
            }
        
        log('Zero instance count detected, recalling.')
        return self.grind_one(check_zero_instance=check_zero_instance)


    def instance_fit_in(self, foreground_img, background_img, x_offset, y_offset):
        '''
        Insertion of instances into the background.
        '''
        # if foreground_img.shape[0] > background_img.shape[0] or foreground_img.shape[1] > background_img.shape[1]:
        #     return 
        
        output = background_img.copy()
        x_min = max(x_offset, 0)
        y_min = max(y_offset, 0)
        x_max = min(background_img.shape[0], x_offset + foreground_img.shape[0])
        y_max = min(background_img.shape[1], y_offset + foreground_img.shape[1])

        for i in range(x_min, x_max):
            for j in range(y_min, y_max):
                for k in range(3):
                    # 使用alpha来抗锯齿
                    alpha = float(foreground_img[i - x_offset][j - y_offset][3]) / 255
                    if alpha < 0.1:
                        continue
                    output[i][j][k] = foreground_img[i - x_offset][j - y_offset][k] * alpha + background_img[i][j][k] * (1 - alpha)
        return output


    def alpha_cutoff(self, foreground_img, ratio=1.0):
        '''
        Does this really matter?
        '''
        output = cv2.resize(foreground_img, dsize=(int(foreground_img.shape[0] * ratio), int(foreground_img.shape[1] * ratio)))
        if foreground_img.shape[2] < 4:
            return
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
        # print(output)
        return output
    

    def get_mask(self, foreground_img, background_img, x_offset, y_offset, color_value):
        # if foreground_img.shape[0] > background_img.shape[0] or foreground_img.shape[1] > background_img.shape[1]:
        #     return
        
        output = background_img.copy()
        x_min = max(x_offset, 0)
        y_min = max(y_offset, 0)
        x_max = min(background_img.shape[0], x_offset + foreground_img.shape[0])
        y_max = min(background_img.shape[1], y_offset + foreground_img.shape[1])

        for i in range(x_min, x_max):
            for j in range(y_min, y_max):
                # 1. 背景的值为0
                # 2. 通道0的值表示相对靠上的图层的透明度
                # 3. 通道1的值代表相对靠下的图层的透明度
                # 4. 如果当前像素同时作为两个以上实例的边缘，则认为相对靠下的图层透明度为1
                if foreground_img[i - x_offset][j - y_offset][3] < 0.1:
                    continue
                output[i][j][2] = foreground_img[i - x_offset][j - y_offset][3]
                output[i][j][0] = color_value

                # 针对半透明区域的交叠标注，不知道为什么总是出问题，暂时还是不处理了 
                # if foreground_img[i - x_offset][j - y_offset][3] > 254:
                #     continue
                # output[i][j][1] = background_img[i - x_offset][j - y_offset][0]
        return output


    def get_pseudo_mask(self, background_image, output, blending_map):
        for i in range(2):
            if background_image.shape[i] != output.shape[i] or background_image.shape[i] != blending_map.shape[i]:
                print('Pseudo mask generation fail and out.')
                return
        for i in range(background_image.shape[0]):
            for j in range(background_image.shape[1]):
                for k in range(3):
                    if output[i][j][k] != background_image[i][j][k]:
                        alpha = float(blending_map[i][j][0]) / 255
                        output[i][j][k] = background_image[i][j][k] * (1 - alpha) + output[i][j][k] * alpha
        return output
    

    def get_pixel_count(self, foreground_image):
        '''Get labels, in form of a dictionary array.'''
        res = 0
        for i in range(foreground_image.shape[0]):
            for j in range(foreground_image.shape[1]):
                if foreground_image[i][j][3] > 0:
                        res += 1
        return res
    

    def get_labels(self, instance_mask, instance_infos):
        '''
        Not that Accurate.
        '''
        # print(len(labels))
        for i in range(instance_mask.shape[0]):
            for j in range(instance_mask.shape[1]):
                pixel = int(instance_mask[i][j][0])
                if pixel < 0.1:
                    continue
                # print(pixel)s
                instance_info = instance_infos[pixel-1]
                instance_info['x_min'] = min(instance_info['x_min'], i / instance_mask.shape[0])
                instance_info['y_min'] = min(instance_info['y_min'], j / instance_mask.shape[1])
                instance_info['y_max'] = max(instance_info['y_max'], j / instance_mask.shape[1])
                instance_info['x_max'] = max(instance_info['x_max'], i / instance_mask.shape[0])
                instance_info['p_cnt'] += 1
        return instance_infos
    

    def get_one_background(self):
        res = random.choice(self._background_imgs)
        return res
    

    def get_one_foreground(self, key):
        res = random.choice(self._foreground_imgs[key])
        return res        


    def get_one_foreground_key(self):
        res = random.choice(list(self._foreground_imgs.keys()))
        return res

if __name__ == '__main__':
    background_root = r'C:\Users\hanyo\Desktop\paramization\outputs\dateset_2024-11-11-12-37-16'
    foreground_root = r'C:\tmp'
    g = Grinder(background_root=background_root, foreground_root=foreground_root)
    g.grind_one()