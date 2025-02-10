# coding=utf-8
# author=lyapunov

'''
randomizor用于生成随机参数, 诸如摄像机的角度参数等.
'''

import os 
import math
import random

from mathutils import Vector

from bpy_scripts.blend_loader import BlendLoader, AssetNotFoundException
from bpy_scripts.scene_setups import SceneSetups
from utils.config_loader import ConfigLoader
from utils.log_writer import LogWriter


class Randomizor():
    ''''''
    def __init__(self):
        # 此处应使用numpy当中的函数来增加可用的随机数分布模式.
        self._ran = random.Random()
        self._bll = BlendLoader()
        self._cfl = ConfigLoader()
        self._ssp = SceneSetups()
        self._models = {}
        # 
        model_folder = self._cfl.get('paths/model-folder')
        foregrounds = self._cfl.get('paths/foreground')
        for root in foregrounds.keys():
            self._models[root] = []
            t_path = os.path.join(model_folder, root)
            # print(t_path)
            for r, d, f in os.walk(t_path):
                # print(f)
                for m in f:
                    if m.endswith('.blend'):
                        self._models[root].append(os.path.join(r, m).replace('\\', '/'))
        # print(self._models)
        # print(self._models.keys())


    def randomize_camera(self):
        cam_name = self._cfl.get('names/camera')
        col_name = self._cfl.get('names/model-collection')
        target_col = self._bll.get_collection(col_name, create_if_null=False)
        if not target_col:
            raise AssetNotFoundException('collection', col_name)
        
        # 1. 设置摄像机
        centric_point = self._bll.get_centric_point(target_col.all_objects)
        dims = self._bll.get_dimensions(target_col.objects)
        width = math.sqrt(dims.x ** 2 + dims.y ** 2  + dims.z ** 2 * 4)
        d_camera = self._bll.get_camera_params(cam_name)
        if not d_camera:
            raise AssetNotFoundException('camera', cam_name)
        distance = width * d_camera.lens / d_camera.sensor_width
        cam_rot_x = random.random() * math.pi / 2
        cam_rot_z = random.random() * math.pi * 2

        self._ssp.set_camera_look_at(Vector((cam_rot_x, 0, cam_rot_z)), centric_point, distance, cam_name)
        

    def randomize_all(self, seed=0, use_default=False):
        '''
        Do not use seed if seed==0.
        Use default params settings rather than randomization.
        '''
        cam_name = self._cfl.get('names/camera')
        sun_name = self._cfl.get('names/sun')
        col_name = self._cfl.get('names/model-collection')
        target_col = self._bll.get_collection(col_name, create_if_null=False)
        if not target_col:
            raise AssetNotFoundException('collection', col_name)
        
        # 1. 设置摄像机
        centric_point, dims = self._bll.get_bounding_box()
        width = math.sqrt(dims.x ** 2 + dims.y ** 2  + dims.z ** 2 * 4)
        d_camera = self._bll.get_camera_params(cam_name)
        if not d_camera:
            raise AssetNotFoundException('camera', cam_name)
        distance = width * d_camera.lens / d_camera.sensor_width
        cam_rot_x = random.random() * math.pi / 2
        cam_rot_z = random.random() * math.pi * 2
        self._ssp.set_camera_look_at(Vector((cam_rot_x, 0, cam_rot_z)), centric_point, distance, cam_name)
        cam_loc = self._bll.get_object(cam_name).location

        # 2. 设置环境光照
        sun_rot_x = random.random() * math.pi / 2
        sun_rot_z = random.random() * math.pi * 2
        self._ssp.set_lighting(Vector((sun_rot_x, 0, sun_rot_z)), None, None, sun_name)
        # 3. 返回标签字典.
        res = {
            'cam_loc_x': cam_loc.x,
            'cam_loc_y': cam_loc.y,
            'cam_loc_z': cam_loc.z,
            'cam_rot_x': cam_rot_x,
            'cam_rot_z': cam_rot_z,
            'cam_distance': distance,
            'sun_rot_x': sun_rot_x,
            'sun_rot_z': sun_rot_z,
            'sun_intensity': None,
            'env_intensity': None,
        }

        return res
    

    def set_distribution(self, d_type):
        return self

    def set_seed(self, seed=None):
        self._ran.seed(seed)
        return self

    def get_random_files(self):
        '''
        Return single string when count==0.
        '''
        classification = self._ran.choice(list(self._models.keys()))
        print(classification)
        blend_path = self._ran.choice(self._models[classification])
        return classification, blend_path


if __name__ == '__main__':
    rdr = Randomizor()
    print(rdr.get_params(100))