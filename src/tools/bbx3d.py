import bpy
import os
import time
from mathutils import Vector


MODEL_COL_NAME = 'model'
BBX_NAME = 'bounding_box'
ROOT_FOLDER = 'C:/Users/hanyo/Documents/Hatuki/Github/de-mirage/src/fragmentor/assets/models'


def batch_create_bbx(root_folder = ROOT_FOLDER):
    file_paths = []
    for r, d, f in os.walk(root_folder):
        for file in f:
            if not file.endswith('.blend'):
                continue
            file_paths.append(os.path.join(r, file))
    total = len(file_paths)
    print(f'Scanning done with {total} blend files found.')
    idx = 0
    start = time.time()
    for file_path in file_paths:
        bpy.ops.wm.open_mainfile(filepath=file_path)
        create_bounding_box()
        print(f'{idx+1} of {total} blend files done.')
        print(f'With {time.time() - start} seconds elapsed.\n')
        idx += 1
        bpy.ops.wm.save_mainfile()
    

def create_bounding_box():
    target_objects = bpy.data.collections.get(MODEL_COL_NAME).all_objects
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

    # 空物体
    axis = bpy.data.objects.get(BBX_NAME)
    if not axis:
        axis = bpy.data.objects.new(BBX_NAME, None)
        bpy.context.scene.collection.objects.link(axis)
    axis.location = Vector(((max_x + min_x) / 2, (max_y + min_y) / 2, (max_z + min_z) / 2))
    axis.scale = Vector((max_x - min_x, max_y - min_y, max_z - min_z))


if __name__ == '__main__':
    batch_create_bbx()