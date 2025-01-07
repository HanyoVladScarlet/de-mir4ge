import bpy 
import os
from mathutils import Vector

from utils.config_loarder import ConfigLoader
from utils.paths import join_paths
from utils.singleton import Singleton

DEFAULT_PATH = 'C:/Users/hanyo/Documents/Hatuki/Github/blender-demo/blends/Mercedes_A-class_5-door_2010.blend'
ATMOSPHERE_NAME = 'PSA-1.81-addon-EN.zip'


@Singleton
class BlendLoader():
    '''
    Use this class to open or load a new blend file.
    And append assets from other blend files.
    '''
    def __init__(self):
        self._cfl = ConfigLoader()
        self.initialize()

    def initialize(self):
        addons = bpy.context.preferences.addons.keys()
        print(bpy.app.version)
        print(addons)
        # PSA
        t_addon = bpy.context.preferences.addons.get('physical-starlight-atmosphere')
        if t_addon is None:
            file_path = join_paths(self._cfl.get('paths/addon-folder'), ATMOSPHERE_NAME)
            bpy.ops.preferences.addon_install(filepath=file_path)
            bpy.ops.preferences.addon_enable(module='physical-starlight-atmosphere')
            bpy.ops.wm.save_userpref()
            t_addon = bpy.context.preferences.addons.get('physical-starlight-atmosphere')
            if t_addon is None:
                raise Exception('PSA does not exist and fails to install!')
        else:
            print('PSA is satisfied.')

    def load_blend_file(self, filepath):
        bpy.ops.wm.open_mainfile(filepath=filepath)
        # 在打开一个新文件时, 防止设置意外变更, 重新设置渲染偏好.
        bpy.context.preferences.addons["cycles"].preferences.get_devices()
        # OPTIX is faster than CUDA.
        bpy.context.preferences.addons['cycles'].preferences. compute_device_type = 'OPTIX'
        for device in bpy.context.preferences.addons['cycles']. preferences.devices:
            if 'nvidia' in device.name.lower():
                device.use = True
                # print(device.name)
                # print(device)
        bpy.context.scene.cycles.device = 'GPU'
        # Make this adaptive.
        # print(bpy.context.preferences.addons['cycles'].preferences. compute_device_type)
        return self

    def append_collections(self, file_path, col_name):
        '''
        Append a collection from a blend file.
        '''
        file_path = os.path.abspath(file_path)
        # print(f'File path is {file_path}')
        target_col = bpy.data.collections.get(col_name)
        if target_col:
            for o in target_col.all_objects:
                o.select_set(True)
            bpy.ops.object.delete()
            mats = [m for m in bpy.data.materials]
            print(mats)
            for m in mats:
                bpy.data.materials.remove(m, do_unlink=True)
        with bpy.data.libraries.load(file_path) as (data_from, data_to):
            if col_name in data_from.collections:
                # 以下删除原来的target_col集合，防止重命名等异常发生导致意外错误.
                if col_name in bpy.data.collections.keys():
                    bpy.data.collections.remove(target_col, do_unlink=True)
                # 添加到本工程文件.
                data_to.collections.append(col_name)
        target_col = self.get_collection(col_name)
        bpy.context.scene.collection.children.link(target_col)
        return self
            

    def append_materials(self, file_path, mat_names):
        with bpy.data.libraries.load(file_path) as (data_from, data_to):
            for mat_name in mat_names:
                if mat_name in data_from.materials:
                    data_to.materials.append(mat_name)
        return self


    def get_collection(self, col_name, create_if_null=True):
        '''
        Get a collection by name.
        Enable create_if_null to create one if not exists.
        '''
        res = bpy.data.collections.get(col_name)
        if not res and create_if_null:
            res = bpy.data.collections.new(col_name)
        return res
    
    def get_object(self, o_name):
        res = bpy.data.objects.get(o_name)
        return res
    
    def get_centric_point(self, target_objects):
            '''
            Geometric center of all these objects.
            TODO: Use a better algorithm.
            '''
            sum_x = 0
            sum_y = 0
            sum_z = 0
            cnt = 0
            for o_target in target_objects:
                if o_target and o_target.type == 'MESH':
                    for v in o_target.data.vertices:
                        co3d = o_target.matrix_world @ v.co
                        sum_x += co3d.x
                        sum_y += co3d.y
                        sum_z += co3d.z
                        cnt += 1

            return Vector((sum_x / cnt, sum_y / cnt, sum_z / cnt))
    
    def get_dimensions(self, target_objects):
        max_x = 0
        max_y = 0
        max_z = 0
        min_x = 0
        min_y = 0
        min_z = 0
        for o_target in target_objects:
            if o_target and o_target.type == 'MESH':
                for v in o_target.data.vertices:
                    co3d = o_target.matrix_world @ v.co
                    max_x = max(co3d.x, max_x)
                    max_y = max(co3d.y, max_y)
                    max_z = max(co3d.z, max_z)
                    min_x = min(co3d.x, min_x)
                    min_y = min(co3d.y, min_y)
                    min_z = min(co3d.z, min_z)
        return Vector((max_x - min_x, max_y - min_y, max_z - min_z))        

    def get_camera_params(self, cam_name='Camera'):
        res = bpy.data.cameras.get(cam_name)
        return res
    
    def get_all_objects(self):
        '''
        Return all objects.
        '''
        return bpy.data.objects

class AssetNotFoundException(BaseException):
    def __init__(self, type, name):
        self._type = type
        self._name = name
    
    def __str__(self):
        return f'Target {self._type} named {self._name} could not resolve, check either config file or blend file.'


if __name__ == '__main__':
    bll = BlendLoader()
    # bll.load_blend_file(DEFAULT_PATH)
    bll.append_collections(DEFAULT_PATH, 'model')
    print(bpy.data.objects.keys())