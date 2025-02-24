import json
import os
import random
import time
import multiprocessing

from datetime import datetime as dt
from PIL import Image


from utils.config_loader import ConfigLoader
from utils.logger import info


# @Singleton
class Grinder():
    ''''''
    def __init__(self):
        self._cfl = ConfigLoader()
        background_roots = self._cfl.get('paths/background')
        foreground_roots = self._cfl.get('paths/foreground')
        output_path = self._cfl.get('paths/output')
        name = dt.now().strftime('output_%Y-%m-%d-%H-%M-%S')
        self._output_image_path = os.path.join(output_path, name, 'images')
        self._output_mask_path = os.path.join(output_path, name, 'masks')
        self._output_label_path = os.path.join(output_path, name, 'labels')
        self._output_config_path = os.path.join(output_path, name, 'config.json')
        self._alpha_max = self._cfl.get('params/alpha_max')
        self._alpha_min = self._cfl.get('params/alpha_min')
        self._boundary_threshold = self._cfl.get('params/boundary_threshold')
        self._instance_count_max = self._cfl.get('params/instance_count_max') 
        self._instance_count_min = self._cfl.get('params/instance_count_min')
        self._occlusion_threshold = self._cfl.get('params/occlusion_threshold')
        self._output_count = self._cfl.get('params/output_count')
        # instance占据background_img最大的比例 (取比例更大的边为准).
        self._size_ratio_upper = self._cfl.get('params/size_ratio_upper')
        self._target_width = self._cfl.get('params/target_width')
        self._target_height = self._cfl.get('params/target_height')
        self._brokens = []
        self._t_start = time.time()
        self._background_imgs = {}
        self._foreground_imgs = {}
        for key in background_roots.keys():
            t_paths = []
            for root, _, files in os.walk(background_roots[key]):
                for file in files:
                    if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.tif'):
                        t_paths.append(os.path.join(root, file))
            self._background_imgs[key] = t_paths
                
        for key in foreground_roots.keys():
            t_paths = []
            for root, _, files in os.walk(foreground_roots[key]):
                for file in files:
                    if file.endswith('.png') or file.endswith('.jpg') or file.endswith('.tif'): 
                        t_paths.append(os.path.join(root, file))
            self._foreground_imgs[key] = t_paths
        if not os.path.exists(self._output_image_path):
            os.makedirs(self._output_image_path)
        if not os.path.exists(self._output_label_path):
            os.makedirs(self._output_label_path)
        if not os.path.exists(self._output_mask_path):
            os.makedirs(self._output_mask_path)


    def grind(self, multi_proc = True):
        ''''''
        with open(self._output_config_path, 'w+') as f:
            f.write(json.dumps(self._cfl._conf))
        core_count = multiprocessing.cpu_count() 
        is_exit = False
        for count in range(0, self._output_count, core_count):
            try:
                pool = multiprocessing.Pool()
                pool.map(self.grind_one, [i for i in range(count, count + core_count)])
                pool.close()
                pool.join()
            except KeyboardInterrupt as e:
                a = 4 / 0
                print(a)
        for file in self._brokens:
            os.remove(file)
            print(f'Obsolete file `{file}` has been removed.')

    def grind_one(self, idx):
        t_start = time.time()
        res = None
        while res is None:
            try:
                res = self.grind_one_image()
            except:
                continue
        name = res['name']
        self.grind_one_label(name, res)
        info(f'{idx + 1} of {self._output_count} images accomplish grinding within {time.time() - t_start}.\nSum up to {(time.time()-self._t_start)} seconds have elapsed.\n')
        return

    def grind_one_image(self):
        t_start = time.time()
        name = f'{str(int(dt.now().timestamp()))}-{os.getpid()}'
        p_image = os.path.join(self._output_image_path, f'{name}.png')
        p_mask = os.path.join(self._output_mask_path, f'{name}.png')
        try:
            # 导入background_img.
            bgi_cls = random.choice(list(self._background_imgs.keys()))
            background = random.choice(self._background_imgs[bgi_cls])
            res = {
                'name': name,
                'p_bgi': background,
            }
            image = self.get_background(background)
            bgi_width, bgi_height = image.size
            mask = Image.new('L', image.size, 0)
            # 设定实例数量.
            if self._instance_count_max != self._instance_count_min:
                count = random.randint(self._instance_count_min, self._instance_count_max)
            else:
                count = self._instance_count_max
            # 初始化标签字典.
            res.update({
                'bgi_cls': bgi_cls,
                'ins_cnt': count,
                'ins_arr': []
            })
            # 添加instance到底图.
            for i in range(count):
                # 选择实例.
                ins_cls = random.choice(list(self._foreground_imgs.keys()))
                foreground = random.choice(self._foreground_imgs[ins_cls])
                instance = Image.open(foreground)
                ins_width, ins_height = instance.size
                ratio = self._size_ratio_upper - random.random() * (self._size_ratio_upper - max(self._boundary_threshold / bgi_height, self._boundary_threshold /  bgi_width))
                instance = instance.resize((int(ins_width * ratio), int(ins_height * ratio)))
                offset_width = int(random.random() * (1 - ratio) * ins_width)
                offset_height = int(random.random() * (1 - ratio) * ins_height)
                ins_width, ins_height = instance.size
                # 调整instance的alpha通道. 
                alpha_map = instance.split()[-1]
                alpha_value = random.random() * (self._alpha_max - self._alpha_min) + self._alpha_min
                alpha_map.putdata([a * alpha_value for a in list(alpha_map.getdata())])
                instance_ext = Image.new('RGBA', image.size, (0, 0, 0, 0))
                instance.putalpha(alpha_map)
                instance_ext.paste(instance, (offset_width, offset_height))
                image = Image.alpha_composite(image, instance_ext)
                # 计算mask对应的r_value.
                r_value = 255 // count * (i + 1) 
                ins_mask = Image.new('RGBA', instance.size, (r_value, 0, 0, 0))
                ins_mask.putalpha(alpha_map)
                o_cnt = 1
                for i in range(ins_mask.width):
                    for j in range(ins_mask.height):
                        _, _, _, a = ins_mask.getpixel((i, j))
                        x = offset_width + i
                        y = offset_height + j
                        if a < 0.1 or x >= mask.width or y >= mask.height:
                            continue
                        mask.putpixel((x, y), r_value)
                        o_cnt += 1
                # 添加实例信息.
                res['ins_arr'].append({
                    'cls': ins_cls,
                    'file': foreground,
                    'o_cnt': o_cnt,
                    'p_cnt': 0,
                    'r_val': r_value,
                    'x_max': 0,
                    'x_min': mask.width,
                    'y_max': 0,
                    'y_min': mask.height,
                    'alpha': alpha_value,
                })
            # 导出图像和遮罩.
            image.save(p_image, icc_profile=None)
            mask.save(p_mask, icc_profile=None)

            # 由于
            for i in range(mask.width):
                for j in range(mask.height):
                    r = mask.getpixel((i, j))
                    for ins in res['ins_arr']:
                        if ins['r_val'] == r:
                            ins['x_min'] = min(i, ins['x_min'])
                            ins['x_max'] = max(i, ins['x_max'])
                            ins['y_min'] = min(j, ins['y_min'])
                            ins['y_max'] = max(j, ins['y_max'])
                            ins['p_cnt'] += 1

            for i in range(count):
                ins = res['ins_arr'][i]
                ins['o_rate'] = 1 - ins['p_cnt'] / ins['o_cnt']
            res['time'] = time.time() - t_start
        except:
            # 标记多余图像.
            self._brokens.append(p_mask)
            self._brokens.append(p_image)
        return res


    def grind_one_label(self, name, content): 
        name = os.path.join(self._output_label_path, name + '.json')
        with open(name, 'w+') as f:
            content = json.dumps(content)
            f.write(content)
        return
    

    def get_background(self, key):
        '''
        
        '''
        res = Image.open(key)
        width, height = res.size
        ratio = max(self._target_width / width, self._target_height / height)
        upper_ratio = max(ratio * 1.2, 1)
        ratio = (upper_ratio - ratio) * random.random() + ratio
        res = res.resize((int(width * ratio), int(height * ratio)))
        width, height = res.size
        offset_width = int(random.random() * (width - self._target_width))
        offset_height = int(random.random() * (height - self._target_height))
        box = (offset_width, offset_height, self._target_width + offset_width, self._target_height + offset_height)
        res = res.crop(box) 
        res = res.convert('RGBA')
        return res


if __name__ == '__main__':
    g = Grinder('hao')
    res = g.grind_one()